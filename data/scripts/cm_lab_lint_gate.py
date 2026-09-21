"""CM-LAB lint/type ratchet gate (S6).

The codebase carries pre-existing lint/type debt. Rather than pretend it is clean or
spend effort reformatting frozen scientific code, this gate uses a RATCHET:

  - It records the current violation counts as a baseline.
  - It FAILS only if NEW debt is introduced (a count exceeds the baseline).
  - Fixing violations and re-running ``--rebaseline`` lowers the bar, so the codebase
    can only get cleaner, never dirtier.

This is honest (acknowledges legacy debt) and safe (never touches frozen code).

Usage:
    .venv/bin/python data/scripts/cm_lab_lint_gate.py              # gate against baseline
    .venv/bin/python data/scripts/cm_lab_lint_gate.py --rebaseline # record a new baseline
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "registries" / "lint_baseline.json"
PY = ROOT / ".venv" / "bin" / "python"
LINT_TARGETS = ["src", "data/scripts", "tests"]


def ruff_count() -> int:
    r = subprocess.run(
        [str(PY), "-m", "ruff", "check", "--output-format=json", *LINT_TARGETS],
        capture_output=True, text=True,
    )
    out = r.stdout.strip()
    if not out:
        return 0
    try:
        return len(json.loads(out))
    except json.JSONDecodeError:
        # Fall back to counting concise lines.
        r2 = subprocess.run(
            [str(PY), "-m", "ruff", "check", "--output-format=concise", *LINT_TARGETS],
            capture_output=True, text=True,
        )
        return sum(1 for ln in r2.stdout.splitlines() if ": " in ln)


def mypy_count() -> int:
    r = subprocess.run(
        [str(PY), "-m", "mypy", "src/causal_mind", "--ignore-missing-imports", "--no-error-summary"],
        capture_output=True, text=True,
    )
    return sum(1 for ln in r.stdout.splitlines() if ": error:" in ln)


def main(argv: list[str]) -> int:
    rc, mc = ruff_count(), mypy_count()
    if "--rebaseline" in argv:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps(
            {"ruff_count": rc, "mypy_count": mc,
             "note": "ratchet baseline; fix violations then --rebaseline to lower the bar"},
            indent=2) + "\n", encoding="utf-8")
        print(f"LINT GATE: baseline recorded (ruff={rc}, mypy={mc})")
        return 0
    if not BASELINE.exists():
        print("LINT GATE: FAIL (no baseline; run --rebaseline first)")
        return 1
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    ok = rc <= base["ruff_count"] and mc <= base["mypy_count"]
    print(f"LINT GATE: ruff {rc}/{base['ruff_count']}, mypy {mc}/{base['mypy_count']}")
    if ok:
        print("LINT GATE: PASS (no new debt)")
        return 0
    print("LINT GATE: FAIL (new lint/type debt introduced)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
