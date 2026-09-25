"""Human-data guard (CM-REPO S43).

Hard-fails if real human participant data is staged into Git. CM-8 will
produce human thought streams; until the human/ethics gate is passed, NO real
human data may enter the repository.

Design (conservative, low false-positive):
* PRIMARY signal -- a tracked file lives in a known human-data directory
  (``data/cm8p/``, ``data/human/``, ...). Any file there is flagged.
* SECONDARY signal -- a tracked file under ``data/`` has a data-like name
  (``*participant*``, ``*human_data*``, ...). Consent *form* templates in
  ``docs/ethics/`` are intentionally NOT flagged.
* PII content (email / DOB / participant_id) is used only to *strengthen* the
  reason for a file already caught by the primary/secondary signals -- it never
  triggers a hit on its own, so dataset metadata dates and example strings in
  code/docs do not false-positive.

Wired into ``cm security scan`` and the pre-commit hook.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from causal_mind import paths
from causal_mind.errors import HumanGateViolationError

# Directories where real human data would land (CM-8P pilot, etc.). PRIMARY signal.
HUMAN_DATA_PATH_PATTERNS: tuple[str, ...] = (
    "data/cm8p/",
    "data/human/",
    "data/raw_human/",
    "data/pilot/",
    "data/participants/",
)

# Data-like file names, applied ONLY under data/. SECONDARY signal.
HUMAN_DATA_NAME_PATTERNS: tuple[str, ...] = (
    "*participant*",
    "*human_data*",
    "*raw_human*",
    "*subject_data*",
    "*real_pilot*",
)

# PII markers used only to strengthen a hit already caught above.
_PII_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),  # email
    re.compile(r"\bdate_?of_?birth\b", re.I),
    re.compile(r"\bparticipant_?id\b\s*[:=]\s*[\"']?(?!sim-|sub-|agent-)[A-Za-z0-9-]{2,}", re.I),
)


@dataclass(frozen=True)
class Hit:
    path: str
    reason: str


def _tracked_files(root: Path) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-c", "safe.directory=*", "ls-files"],
            cwd=root, capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [line for line in out.splitlines() if line.strip()]


def _pii_reason(fp: Path) -> str | None:
    """Short PII note for a file already flagged by path/name (or None)."""
    if not fp.is_file() or fp.stat().st_size > 5_000_000:
        return None
    try:
        text = fp.read_text(errors="ignore")
    except OSError:
        return None
    for pat in _PII_PATTERNS:
        if pat.search(text):
            return f"PII marker {pat.pattern[:32]!r}"
    return None


def scan(root: Path | None = None) -> list[Hit]:
    """Return human-data hits among git-tracked files (empty = clean)."""
    root = root or paths.repo_root()
    hits: list[Hit] = []
    for rel in _tracked_files(root):
        # PRIMARY: file in a known human-data directory.
        for pat in HUMAN_DATA_PATH_PATTERNS:
            if rel.startswith(pat):
                reason = f"path in human-data dir {pat!r}"
                pii = _pii_reason(root / rel)
                if pii:
                    reason += f"; {pii}"
                hits.append(Hit(rel, reason))
                break
        else:
            # SECONDARY: data-like name, but only under data/ (not docs/).
            if rel.startswith("data/"):
                name = Path(rel).name.lower()
                for pat in HUMAN_DATA_NAME_PATTERNS:
                    if pat.strip("*").lower() in name:
                        hits.append(Hit(rel, f"filename matches {pat!r} under data/"))
                        break
    return hits


def assert_clean(root: Path | None = None) -> None:
    """Raise :class:`HumanGateViolationError` if any human data is staged."""
    hits = scan(root)
    if hits:
        listing = "\n".join(f"  {h.path}: {h.reason}" for h in hits[:20])
        raise HumanGateViolationError(
            f"human/ethics gate: {len(hits)} file(s) look like real human data "
            f"(must not enter Git before the human gate is passed):\n{listing}",
            details={"hits": [h.path for h in hits]},
        )
