from __future__ import annotations

import re
from dataclasses import dataclass

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private-key-block", re.compile(r"-----BEGIN (RSA|EC|OPENSSH|DSA)? ?PRIVATE KEY-----")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\b")),
    ("bearer-token", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{40,}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("ssh-key-file-ref", re.compile(r"\bid_ed25519\b|\bid_rsa\b")),
    ("kubeconfig-ref", re.compile(r"\bkubeconfig\b.*\byaml\b", re.IGNORECASE)),
    (
        "generic-api-key",
        re.compile(r"(?i)\b(api[_-]?key|secret|token)\b\s*[:=]\s*['\"][A-Za-z0-9._\-]{16,}['\"]"),
    ),
)


@dataclass(frozen=True)
class SecretFinding:
    kind: str
    line_number: int
    snippet: str


def scan_for_secrets(text: str) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(SecretFinding(kind=kind, line_number=lineno, snippet=line[:80]))
    return findings


def assert_no_secrets(text: str) -> None:
    findings = scan_for_secrets(text)
    if findings:
        kinds = sorted({f.kind for f in findings})
        raise ValueError(f"potential secrets detected: {', '.join(kinds)}")
