"""CM-LAB security audit (S75-S84).

Checks the repository for the security properties a professional research platform
must hold, and writes a machine-readable + human-readable report.

Checks:
  1. Secret scan        -- no private keys / cloud keys / tokens / credential literals.
  2. Credential files   -- no SSH keys, .env, .pem, .netrc, k8s/runai creds tracked in git.
  3. Network exposure   -- no service binds to 0.0.0.0 (local tooling binds 127.0.0.1).
  4. Telemetry          -- no outbound POST/PUT of data to external endpoints.
  5. Dependency list    -- inventory of pinned dependencies (for the record).

Usage:
    .venv/bin/python data/scripts/cm_lab_security.py            # audit + write report
    .venv/bin/python data/scripts/cm_lab_security.py --check    # exit non-zero on any FAIL
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports" / "security_audit.json"
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}
SCAN_SUFFIXES = {".py", ".sh", ".json", ".yaml", ".yml", ".md", ".txt", ".toml", ".cfg", ".ini", ".env"}

SECRET_PATTERNS = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key block"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"ghp_[A-Za-z0-9]{36,}", "GitHub personal access token"),
    (r"gho_[A-Za-z0-9]{36,}", "GitHub OAuth token"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI-style secret key"),
    (r"(?i)(api[_-]?key|secret|auth[_-]?token|access[_-]?token|password|passwd|bearer)\s*[:=]\s*['\"][A-Za-z0-9+/=_\-]{16,}['\"]",
     "credential literal"),
]
SAFE_LINE = re.compile(r"(?i)example|placeholder|your[_ ]|<.*>|\bdummy\b|changeme|\bxxx+\b|redacted|yourtoken|yourkey")

CRED_FILE_PATTERNS = [
    r"(?i)^\.env(\.|$)", r"(?i)id_(rsa|ed25519|ecdsa|dsa)$", r"(?i)\.pem$", r"(?i)\.p12$",
    r"(?i)\.pfx$", r"(?i)\.netrc$", r"(?i)credentials\.(json|ya?ml)$", r"(?i)known_hosts$",
    r"(?i)\.runai", r"(?i)kubeconfig", r"(?i)service\.account.*\.json",
]


# Security test fixtures deliberately contain FAKE credentials to verify detection.
SECRET_SCAN_EXCLUDE = re.compile(r"(?i)credential_security|security_test|_secrets?_fixture")


def _iter_files():
    for f in ROOT.rglob("*"):
        if not f.is_file():
            continue
        if any(p in SKIP_DIRS for p in f.parts):
            continue
        if f == REPORT:  # never scan the audit's own output (avoids feedback loop)
            continue
        if f.suffix in SCAN_SUFFIXES:
            yield f


def _iter_files_no_fixtures():
    for f in _iter_files():
        if not SECRET_SCAN_EXCLUDE.search(f.name):
            yield f


def secret_scan() -> list[dict]:
    hits = []
    for f in _iter_files_no_fixtures():
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for pat, label in SECRET_PATTERNS:
                if re.search(pat, line) and not SAFE_LINE.search(line):
                    hits.append({"file": str(f.relative_to(ROOT)), "line": i, "kind": label,
                                 "snippet": line.strip()[:90]})
    return hits


_TEMPLATE = re.compile(r"(?i)\.(example|template|sample|tmpl)$")


def credential_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    hits = []
    for path in out.stdout.splitlines():
        if _TEMPLATE.search(path):  # .env.example etc. are safe templates
            continue
        if any(re.search(p, path) for p in CRED_FILE_PATTERNS):
            hits.append(path)
    return hits


BIND_PAT = re.compile(
    r"(?i)(bind\s*\(\s*\(?\s*['\"]0\.0\.0\.0|host\s*=\s*['\"]0\.0\.0\.0['\"]"
    r"|address\s*=\s*['\"]0\.0\.0\.0['\"]|interface\s*=\s*['\"]0\.0\.0\.0['\"])"
)


def network_exposure() -> list[dict]:
    """Flag actual binds to 0.0.0.0 (not docstrings/prints that merely mention it)."""
    hits = []
    for f in ROOT.rglob("*.py"):
        if any(p in SKIP_DIRS for p in f.parts):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if BIND_PAT.search(line):
                hits.append({"file": str(f.relative_to(ROOT)), "line": i, "snippet": line.strip()[:90]})
    return hits


def telemetry() -> list[dict]:
    hits = []
    for f in ROOT.rglob("*.py"):
        if any(p in SKIP_DIRS for p in f.parts):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"(?i)requests\.(post|put)\s*\(\s*['\"]https?://", line):
                hits.append({"file": str(f.relative_to(ROOT)), "line": i, "snippet": line.strip()[:90]})
    return hits


def dependencies() -> list[str]:
    lock = ROOT / "uv.lock"
    deps = []
    if lock.exists():
        for m in re.finditer(r'name\s*=\s*"([^"]+)"', lock.read_text(encoding="utf-8", errors="ignore")):
            deps.append(m.group(1))
    return sorted(set(deps))


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    secrets = secret_scan()
    creds = credential_files()
    exposure = network_exposure()
    telem = telemetry()
    deps = dependencies()

    result = {
        "secret_scan": {"count": len(secrets), "hits": secrets},
        "credential_files": {"count": len(creds), "hits": creds},
        "network_exposure_0_0_0_0": {"count": len(exposure), "hits": exposure},
        "telemetry_outbound": {"count": len(telem), "hits": telem},
        "n_dependencies": len(deps),
        "dependencies": deps,
    }
    # FAIL conditions: secrets, tracked credential files, or 0.0.0.0 binds.
    failures = []
    if secrets:
        failures.append(f"{len(secrets)} secret hit(s)")
    if creds:
        failures.append(f"{len(creds)} tracked credential file(s)")
    if exposure:
        failures.append(f"{len(exposure)} 0.0.0.0 bind(s)")
    result["status"] = "CMLAB_SECURITY_PASS" if not failures else "CMLAB_SECURITY_FAIL"
    result["failures"] = failures

    if not check_only:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(f"secret scan:        {len(secrets)} hit(s)")
    print(f"credential files:   {len(creds)} tracked")
    print(f"0.0.0.0 binds:      {len(exposure)}")
    print(f"outbound telemetry: {len(telem)}")
    print(f"dependencies:       {len(deps)} pinned")
    if failures:
        print(f"SECURITY: FAIL -> {failures}")
        for s in secrets[:10]:
            print(f"   secret: {s['file']}:{s['line']} [{s['kind']}] {s['snippet']}")
        for c in creds[:10]:
            print(f"   credfile: {c}")
        for e in exposure[:10]:
            print(f"   exposure: {e['file']}:{e['line']} {e['snippet']}")
        return 1
    print("SECURITY: PASS (CMLAB_SECURITY_PASS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
