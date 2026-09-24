"""CM-LAB §61-62: Collaborator reproduction package + supervisor demo mode.

A single entry point that reproduces the scientific deep dive for a new collaborator, or runs a
fast supervisor demo.

Full mode (reproduces every deep-dive result; ~5-10 min on the A100 pod):
    .venv/bin/python data/scripts/cm_deep_dive_runner.py

Demo mode (fast subset for a supervisor walkthrough; ~1 min):
    .venv/bin/python data/scripts/cm_deep_dive_runner.py --demo

Each workstream is a (label, script, report-json) triple. The runner executes the scripts in
order, reads each report's "decision", and prints a consolidated summary. It does NOT re-derive
any result; it invokes the frozen per-workstream scripts (which are the source of truth).

No CM-8 change. No human data.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/jovyan/work/causal-mind-v2")
PY = ROOT / ".venv" / "bin" / "python"
SCRIPTS = ROOT / "data" / "scripts"

# (label, script, report-json, decision-key) for the full deep dive.
FULL = [
    ("S25-28 XVAL inference", "cm_xval_inference.py", "reports/cm_xval/cm_xval_inference.json"),
    ("S32-35 Uncertainty", "cm_uncertainty.py", "reports/cm_uncertainty/cm_uncertainty.json"),
    ("S29-31 Representation", "cm_representation.py", "reports/cm_representation/cm_representation.json"),
    ("S36-40 Personalization", "cm_personalization.py", "reports/cm_personalization/cm_personalization.json"),
    ("S41,43-47 Local dynamics", "cm_dynamics.py", "reports/cm_dynamics/cm_dynamics.json"),
    ("S48-49 Error taxonomy", "cm_error_taxonomy.py", "reports/cm_error_taxonomy/cm_error_taxonomy.json"),
    ("S63-71 Oracle", "cm_oracle.py", "reports/cm_oracle/cm_oracle.json"),
    ("S55 Leakage scan", "cm_leakage_scan.py", "reports/cm_leakage_scan/cm_leakage_scan.json"),
    ("S83 CM-8 no-drift", "cm8_no_drift.py", "reports/cm8_no_drift/cm8_no_drift.json"),
]

# Fast subset for a supervisor demo (no heavy embedding/model fits).
DEMO = [
    ("S55 Leakage scan", "cm_leakage_scan.py", "reports/cm_leakage_scan/cm_leakage_scan.json"),
    ("S83 CM-8 no-drift", "cm8_no_drift.py", "reports/cm8_no_drift/cm8_no_drift.json"),
    ("S52 Randomness audit (report)", None, "reports/cm8r_randomization/cm8r_randomization.json"),
]


def _decision(report_rel: str) -> str:
    p = ROOT / report_rel
    if not p.exists():
        return "NO_REPORT"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return "BAD_JSON"
    return d.get("decision", "NO_DECISION")


def run_one(label: str, script: str | None, report_rel: str) -> tuple[str, str]:
    t0 = time.time()
    if script is not None:
        r = subprocess.run([str(PY), str(SCRIPTS / script)], cwd=ROOT,
                           capture_output=True, text=True)
        status = "OK" if r.returncode == 0 else f"FAIL({r.returncode})"
        if r.returncode != 0:
            print(f"  [FAIL] {label}: {r.stderr.strip().splitlines()[-1] if r.stderr else 'no stderr'}")
    else:
        status = "REPORT_ONLY"
    dec = _decision(report_rel)
    print(f"  [{status}] {label}: {dec} ({time.time() - t0:.1f}s)")
    return status, dec


def main() -> int:
    demo = "--demo" in sys.argv
    workstreams = DEMO if demo else FULL
    mode = "DEMO (fast subset)" if demo else "FULL deep-dive reproduction"
    print("=" * 64)
    print(f" CM-LAB collaborator reproduction - {mode}")
    print("=" * 64)
    t0 = time.time()
    results = []
    for label, script, report in workstreams:
        status, dec = run_one(label, script, report)
        results.append((label, status, dec))
    print("-" * 64)
    n_ok = sum(1 for _, s, _ in results if s in ("OK", "REPORT_ONLY"))
    print(f" {n_ok}/{len(results)} workstreams OK in {time.time() - t0:.1f}s")
    for label, status, dec in results:
        print(f"   {dec:40s} {label}")
    print("=" * 64)
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
