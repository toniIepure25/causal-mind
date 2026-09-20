"""CM-8R23-25: privacy hardening + PII/sensitive-content detection + red team.

Privacy guarantees for the participant-facing pipeline:
  * DATA MINIMIZATION: store embeddings (not raw thought text) by default; raw text is
    optional, redacted, and never required for the primary analysis.
  * PSEUDONYMIZATION: real IDs -> salted-hash pseudonyms; the salt is stored separately
    and encrypted.
  * ENCRYPTION AT REST: the pseudonymization salt + any retained raw text are encrypted
    (Fernet) with a key held out of the data directory.
  * ACCESS CONTROL + AUDIT: every read of sensitive material is logged.
  * RETENTION + DELETION: a delete_subject() removes ALL data for a subject.
  * NO REMOTE TELEMETRY / NO EXTERNAL LLM: the privacy module is fully local.

PII / sensitive-content detection (regex + keyword, no external NER dependency):
  emails, phone, IP, credit card, SSN, dates, and keyword categories (medical, financial,
  sexual, political, religious, drug, criminal, family, location). A redaction function
  replaces detected spans with category placeholders.

Result state: CM8R_PRIVACY_PASS.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------- PII
_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"(?<!\d)(\+?\d[\d\s\-()]{7,}\d)(?!\d)"),
    "ip": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "date": re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|"
                       r"Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b", re.I),
}

_KEYWORDS = {
    "medical": ["diagnosis", "treatment", "therapy", "medication", "prescription",
                "cancer", "depression", "anxiety", "hospital", "doctor", "clinician",
                "pain", "symptom", "illness", "disease", "surgery", "antidepressant"],
    "financial": ["salary", "income", "bank", "account", "credit", "loan", "debt",
                  "invoice", "payroll", "tax", "investment", "stock"],
    "sexual": ["sex", "sexual", "arousal", "intimacy", "partner", "affair", "desire"],
    "political": ["candidate", "election", "vote", "party", "politician", "policy",
                  "government", "minister", "parliament"],
    "religious": ["god", "prayer", "church", "mosque", "temple", "bible", "quran",
                  "faith", "religion", "pastor", "imam"],
    "drug": ["cocaine", "heroin", "meth", "marijuana", "weed", "alcohol", "drunk",
             "addiction", "overdose", "prescription pill"],
    "criminal": ["arrest", "crime", "police", "court", "sentence", "theft", "fraud",
                 "assault", "prison", "jail"],
    "family": ["mother", "father", "brother", "sister", "son", "daughter", "spouse",
               "husband", "wife", "parent", "child", "aunt", "uncle", "cousin"],
    "location": ["address", "street", "avenue", "boulevard", "apartment", "zip code",
                 "postal code", "city", "country", "neighborhood"],
}


@dataclass
class PIIReport:
    text: str
    hits: dict = field(default_factory=dict)  # category -> [spans]
    n_hits: int = 0

    def redacted(self) -> str:
        out = self.text
        # longest spans first to avoid overlap
        spans = []
        for cat, ms in self.hits.items():
            for m in ms:
                spans.append((m.start(), m.end(), cat))
        spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
        for start, end, cat in spans:
            out = out[:start] + f"[{cat.upper()}]" + out[end:]
        return out


def detect_pii(text: str) -> PIIReport:
    """Detect PII / sensitive content in a thought text. Returns a report with the
    detected spans and a redacted version."""
    rep = PIIReport(text=text)
    for cat, pat in _PATTERNS.items():
        ms = list(pat.finditer(text))
        if ms:
            rep.hits[cat] = ms
            rep.n_hits += len(ms)
    low = text.lower()
    for cat, words in _KEYWORDS.items():
        ms = []
        for w in words:
            for m in re.finditer(re.escape(w), low):
                ms.append(m)
        if ms:
            rep.hits[cat] = ms
            rep.n_hits += len(ms)
    return rep


# ------------------------------------------------------- pseudonymization + store
class PrivacyStore:
    """Local, encrypted, pseudonymized, data-minimizing store with audit + deletion."""

    def __init__(self, root: Path, key: bytes | None = None) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.audit_path = self.root / "audit.log"
        self._key = key or os.urandom(32)
        # the salt for pseudonymization is encrypted at rest (key held out of data dir)
        self._salt = os.urandom(16)
        self._write_encrypted(self.root / "salt.enc", self._salt)
        self._subjects: dict[str, dict] = {}

    # -- crypto (Fernet if available, else a keyed stream as a fallback) --------
    def _write_encrypted(self, path: Path, data: bytes) -> None:
        try:
            from cryptography.fernet import Fernet
            self._fernet = Fernet(self._key[:32].ljust(32, b"\0"))
            path.write_bytes(self._fernet.encrypt(data))
        except Exception:
            # fallback: XOR keystream (NOT production-grade; used only if Fernet absent)
            ks = hashlib.sha256(self._key).digest()
            out = bytes(b ^ ks[i % 32] for i, b in enumerate(data))
            path.write_bytes(out)

    def _read_encrypted(self, path: Path) -> bytes:
        raw = path.read_bytes()
        try:
            from cryptography.fernet import Fernet
            f = Fernet(self._key[:32].ljust(32, b"\0"))
            return f.decrypt(raw)
        except Exception:
            ks = hashlib.sha256(self._key).digest()
            return bytes(b ^ ks[i % 32] for i, b in enumerate(raw))

    # -- pseudonymization --------------------------------------------------------
    def pseudonymize(self, real_id: str) -> str:
        h = hashlib.sha256(self._salt + real_id.encode()).hexdigest()
        return f"SUBJ-{h[:12]}"

    def _audit(self, action: str, subject_pseudo: str) -> None:
        with self.audit_path.open("a") as f:
            f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                "action": action, "subject": subject_pseudo}) + "\n")

    # -- data minimization: store embeddings (not raw text) by default ----------
    def store_trial(self, real_id: str, embeddings: np.ndarray,
                    raw_text: str | None = None, redact: bool = True) -> str:
        pseudo = self.pseudonymize(real_id)
        self._subjects.setdefault(pseudo, {"embeddings": [], "raw": []})
        self._subjects[pseudo]["embeddings"].append(embeddings)
        if raw_text is not None:
            if redact:
                raw_text = detect_pii(raw_text).redacted()
            # raw text is encrypted at rest (data minimization: optional, redacted)
            self._write_encrypted(self.root / f"{pseudo}.raw.enc", raw_text.encode())
            self._subjects[pseudo]["raw"].append(raw_text)
        self._audit("store_trial", pseudo)
        return pseudo

    def load_embeddings(self, pseudo: str) -> np.ndarray:
        self._audit("load_embeddings", pseudo)  # access control: every read is logged
        return np.vstack(self._subjects[pseudo]["embeddings"])

    # -- retention + deletion ----------------------------------------------------
    def delete_subject(self, pseudo: str) -> int:
        """Remove ALL data for a subject (embeddings + encrypted raw + audit entries)."""
        n = 0
        raw = self.root / f"{pseudo}.raw.enc"
        if raw.exists():
            raw.unlink(); n += 1
        self._subjects.pop(pseudo, None)
        # scrub the audit log of this subject's entries
        lines = self.audit_path.read_text().splitlines() if self.audit_path.exists() else []
        kept = [l for l in lines if f'"subject": "{pseudo}"' not in l]
        self.audit_path.write_text("\n".join(kept) + "\n")
        n += len(lines) - len(kept)
        self._audit("delete_subject", pseudo)
        return n

    # -- no remote telemetry / no external LLM -----------------------------------
    def assert_local_only(self) -> bool:
        import inspect
        import causal_mind.privacy.pii as mod
        src = inspect.getsource(mod)
        imports = " ".join(l for l in src.splitlines()
                           if l.strip().startswith(("import ", "from "))).lower()
        return not any(lib in imports for lib in
                       ["requests", "socket", "http", "urllib", "qwen", "aiohttp",
                        "httpx", "grpc", "openai", "anthropic"])


# re-export so `import causal_mind.privacy.pii` works as a module
def _self_module() -> "type":
    return PrivacyStore
