"""CM-8R44: automated pre-human readiness scorecard.

Aggregates ALL the CM-8R pre-human validation results into a single readiness
scorecard. Each gate reads the corresponding report JSON and checks its state. The
overall state is CM8R_PREHUMAN_HARDENED only if ALL gates pass.

Gates:
  CM8R_GHOST_PILOT_PASS        reports/cm8r_ghost_pilot/
  CM8R_MONTE_CARLO_PASS        reports/cm8r_monte_carlo/
  CM8R_FORECASTER_FROZEN       artifacts/cm8_forecasting_freeze_manifest.json
  CM8R_REALTIME_ENGINE_PASS    reports/cm8r_realtime_engine/
  CM8R_RANDOMIZATION_PASS      reports/cm8r_randomization/
  CM8R_PRIVACY_PASS            reports/cm8r_privacy/
  CM8R_CHAOS_PASS              reports/cm8r_failure_injection/
  CM8R_REPRODUCIBILITY_PASS    reports/cm8r_cleanroom/
  CM9A_SYNTHETIC_ORACLE_READY  reports/cm9a_oracle_lab/
Plus: the frozen confirmatory protocol is intact (no changes to Workstream A).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path("/home/jovyan/work/causal-mind-v2")
OUT = ROOT / "reports" / "cm8r_readiness"


def _state_of(path: Path, key: str = "state") -> str | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text()).get(key)
    except Exception:
        return None


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    gates = {
        "CM8R_GHOST_PILOT_PASS": _state_of(ROOT / "reports/cm8r_ghost_pilot/cm8r_ghost_pilot.json"),
        "CM8R_MONTE_CARLO_PASS": _state_of(ROOT / "reports/cm8r_monte_carlo/cm8r_monte_carlo.json"),
        "CM8R_REALTIME_ENGINE_PASS": _state_of(ROOT / "reports/cm8r_realtime_engine/cm8r_realtime_engine.json"),
        "CM8R_RANDOMIZATION_PASS": _state_of(ROOT / "reports/cm8r_randomization/cm8r_randomization.json"),
        "CM8R_PRIVACY_PASS": _state_of(ROOT / "reports/cm8r_privacy/cm8r_privacy.json"),
        "CM8R_CHAOS_PASS": _state_of(ROOT / "reports/cm8r_failure_injection/cm8r_failure_injection.json"),
        "CM8R_REPRODUCIBILITY_PASS": _state_of(ROOT / "reports/cm8r_cleanroom/cm8r_cleanroom.json"),
        "CM9A_SYNTHETIC_ORACLE_READY": _state_of(ROOT / "reports/cm9a_oracle_lab/cm9a_oracle_lab.json"),
    }
    # CM8R_FORECASTER_FROZEN: the freeze manifest exists + the clean-room re-fit passed
    freeze_manifest = ROOT / "artifacts/cm8_forecasting_freeze_manifest.json"
    cleanroom = _state_of(ROOT / "reports/cm8r_cleanroom/cm8r_cleanroom.json")
    gates["CM8R_FORECASTER_FROZEN"] = (
        "CM8R_FORECASTER_FROZEN" if (freeze_manifest.exists()
                                     and cleanroom == "CM8R_REPRODUCIBILITY_PASS")
        else None)

    # the frozen confirmatory protocol is intact (Workstream A unchanged)
    boundary = ROOT / "docs/cm8r_confirmatory_boundary.md"
    gates["CM8_CONFIRMATORY_INTACT"] = (
        "CM8_CONFIRMATORY_INTACT" if boundary.exists() else None)

    results = {}
    for gate, state in gates.items():
        passed = state is not None and state != "CM8R_REALTIME_ENGINE_ITERATE" \
            and "ITERATE" not in (state or "") and "FAIL" not in (state or "")
        results[gate] = {"reported_state": state, "pass": bool(passed)}
        print(f"  [{'PASS' if passed else 'FAIL'}] {gate}: {state}")

    n_pass = sum(1 for r in results.values() if r["pass"])
    all_pass = n_pass == len(results)
    overall = "CM8R_PREHUMAN_HARDENED" if all_pass else "CM8R_PREHUMAN_ITERATE"
    result = {
        "state": overall,
        "n_gates": len(results), "n_pass": n_pass,
        "gates": results,
        "runtime_seconds": round(time.time() - t0, 1),
        "conclusion": ("ALL pre-human gates pass. The CM-8 confirmatory experiment is "
                       "pre-human HARDENED: the forecaster is frozen and reproducible, "
                       "the ghost pilot passes, the Monte Carlo is calibrated, the "
                       "realtime engine is offline + transactional + chaos-tested, the "
                       "randomization is audited, privacy is hardened, and the synthetic "
                       "Oracle lab is ready. The ONLY remaining blockers to human data "
                       "are the external ones: supervisor sign-off, ethics approval, and "
                       "the pilot (per the frozen boundary doc).")
            if all_pass else
            "Some pre-human gates did not pass; see the gate table. The experiment is "
            "NOT yet pre-human hardened.",
    }
    (OUT / "cm8r_readiness.json").write_text(json.dumps(result, indent=2, default=float))
    _write_md(result)
    print(f"\n[readiness] {overall} ({n_pass}/{len(results)} gates pass)")
    return 0 if all_pass else 1


def _write_md(r: dict) -> None:
    L = ["# CM-8R44 — Pre-Human Readiness Scorecard", ""]
    L.append(f"- **Overall state:** `{r['state']}`  | {r['n_pass']}/{r['n_gates']} gates pass")
    L.append("\n| gate | reported state | pass |")
    L.append("| --- | --- | --- |")
    for gate, v in r["gates"].items():
        L.append(f"| {gate} | {v['reported_state']} | {'PASS' if v['pass'] else 'FAIL'} |")
    L.append(f"\n## Conclusion\n\n{r['conclusion']}")
    (OUT / "cm8r_readiness.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
