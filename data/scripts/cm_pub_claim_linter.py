"""CM-PUB claim-language linter.

Scans markdown/text sources for overclaiming language and reports hits. Part of the
cm8-prehuman-v1.0 freeze. The goal is to enforce the claims-registry discipline:

  - No free-will claim (proven or disproven).
  - No causal claim from observational data.
  - No lower-level result worded as a higher-level one.

Usage:
    .venv/bin/python data/scripts/cm_pub_claim_linter.py [paths ...]

If no paths are given, it scans docs/ and papers/. Exit code 1 if any BLOCK-level hit is
found, 0 otherwise. WARN-level hits are reported but do not fail the run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# (level, pattern, why)
# level: "BLOCK" fails the run; "WARN" is reported only.
RULES: list[tuple[str, str, str]] = [
    # --- free-will / consciousness claims (always BLOCK) ---
    ("BLOCK", r"prove[sd]? (that )?(the existence of )?free will", "free-will claim (proven)"),
    ("BLOCK", r"disprove[sd]? (that )?(the existence of )?free will", "free-will claim (disproven)"),
    ("BLOCK", r"free will (is|was|has been) (proven|disproven|established|demonstrated)", "free-will claim"),
    ("BLOCK", r"prove[sd]? (that )?(we|humans|people) (have|do not have|lack) free will", "free-will claim"),
    ("BLOCK", r"the oracle (proves|demonstrates|establishes)", "oracle overclaim"),
    ("BLOCK", r"prove[sd]? (that )?consciousness (exists|is real)", "consciousness claim"),

    # --- causal overclaims (BLOCK unless in a validated-randomized context) ---
    ("BLOCK", r"prove[sd]? (that )?.{0,60} (causes|causation)", "causal overclaim (proves causation)"),
    ("BLOCK", r"demonstrate[sd]? (that )?.{0,60} (causes|causation)", "causal overclaim (demonstrates causation)"),
    ("BLOCK", r"establishes? (that )?.{0,60} (causes|causation)", "causal overclaim (establishes causation)"),

    # --- strong-verb overclaims (WARN; review context) ---
    ("WARN", r"\bproves?\b", "strong verb 'prove' (check level)"),
    ("WARN", r"demonstrates? conclusively", "conclusive demonstration (check level)"),
    ("WARN", r"definitively (shows|demonstrates|establishes|proves)", "definitive claim (check level)"),
    ("WARN", r"irrefutabl", "irrefutable claim (check level)"),
    ("WARN", r"beyond (any )?reasonable doubt", "legal-standard overclaim"),

    # --- observational-data causal language (BLOCK) ---
    ("BLOCK", r"observational.{0,80}(causal effect|causally identifies|proves causation)", "causal claim from observational data"),
]

_COMPILED = [(lvl, re.compile(pat, re.IGNORECASE), why) for lvl, pat, why in RULES]

# Lines that are explicitly about REFUSING/NOT claiming are safe (negation context).
_NEGATION = re.compile(
    r"(no|not|without|refus|does not|do not|never|avoid|without making|no free-will|no causal|"
    r"not a|not yet|cannot|can't|without a|absent|gated|blocked|not claim|no claim|"
    r"we make no|we do not|not made|not implied|out of scope|not a claim|never worded|"
    r"never claim|no free-will claim|no causal claim|no overclaim)",
    re.IGNORECASE,
)


def _is_negated(line: str) -> bool:
    return bool(_NEGATION.search(line))


def scan_file(path: Path) -> list[tuple[str, int, str, str]]:
    hits: list[tuple[str, int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return hits
    for i, line in enumerate(text.splitlines(), 1):
        for lvl, rx, why in _COMPILED:
            if rx.search(line):
                # A negation in the same line downgrades BLOCK -> WARN (it is a
                # statement about NOT making the claim).
                eff = lvl
                if lvl == "BLOCK" and _is_negated(line):
                    eff = "WARN"
                hits.append((eff, i, why, line.strip()[:120]))
    return hits


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parents[2]
    if argv:
        targets = [Path(a) for a in argv]
    else:
        targets = [root / "docs", root / "papers"]

    all_hits: list[tuple[str, int, str, str, Path]] = []
    for t in targets:
        files = [t] if t.is_file() else sorted(t.rglob("*"))
        for f in files:
            if f.is_file() and f.suffix in {".md", ".txt", ".rst"}:
                for lvl, ln, why, snippet in scan_file(f):
                    all_hits.append((lvl, ln, why, snippet, f))

    blocks = [h for h in all_hits if h[0] == "BLOCK"]
    warns = [h for h in all_hits if h[0] == "WARN"]

    for lvl, ln, why, snippet, f in sorted(all_hits, key=lambda h: (h[4], h[1])):
        rel = f.relative_to(root) if f.is_relative_to(root) else f
        print(f"[{lvl}] {rel}:{ln}: {why}\n        {snippet}")

    print(f"\n{len(blocks)} BLOCK, {len(warns)} WARN across {len(all_hits)} hits.")
    if blocks:
        print("RESULT: FAIL (overclaiming language detected)")
        return 1
    print("RESULT: PASS (no BLOCK-level overclaims)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
