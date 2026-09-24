"""CM-LAB §83: CM-8 confirmatory no-drift verification.

Verifies that the frozen CM-8 confirmatory protocol has NOT drifted since the
`cm8-prehuman-v1.0` freeze. This is a dedicated, self-contained check (no pytest dependency):

  1. Frozen forecaster config values: test_alpha=0.05, basin_tail=0.10,
     primary_horizon_h_star=2, horizons=[1,2,3,4,5,6,8,10], BRP definition intact.
  2. Freeze-manifest code SHAs (predicted_basin.py and the rest) match the on-disk files.
  3. Randomization manifest present and well-formed (seed, B, N, trials).
  4. Config + freeze-manifest + randomization-manifest SHAs match the frozen artifact registry.
  5. No real human-data collection enabled pre-ethics (synthetic pseudonyms only).

Decision: CM8_CONFIRMATORY_INTACT if all pass, else CM8_DRIFT_DETECTED.

Usage:
    .venv/bin/python data/scripts/cm8_no_drift.py
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

ROOT = Path("/home/jovyan/work/causal-mind-v2")
OUT = ROOT / "reports" / "cm8_no_drift"
CFG = ROOT / "artifacts" / "cm8_forecaster" / "config.json"
FREEZE = ROOT / "docs" / "ethics" / "cm8_software_freeze_manifest.json"
RAND = ROOT / "data" / "manifests" / "cm8_randomization_manifest.json"
REGISTRY = ROOT / "registries" / "artifact_registry.json"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    checks: dict = {}
    all_ok = True

    # 1. Frozen forecaster config values.
    cfg = _load(CFG)
    cfg_ok = (
        cfg.get("basin_tail") == 0.1
        and cfg.get("primary_horizon_h_star") == 2
        and cfg.get("horizons") == [1, 2, 3, 4, 5, 6, 8, 10]
        and "outside the basin" in cfg.get("inference", {}).get("brp", "")
        and cfg.get("k_history_depth") == 3
        and cfg.get("ridge_alpha") == 100.0
    )
    checks["forecaster_config"] = {
        "pass": bool(cfg_ok),
        "basin_tail": cfg.get("basin_tail"),
        "h_star": cfg.get("primary_horizon_h_star"),
        "horizons": cfg.get("horizons"),
        "brp_intact": "outside the basin" in cfg.get("inference", {}).get("brp", ""),
        "k": cfg.get("k_history_depth"),
        "ridge_alpha": cfg.get("ridge_alpha"),
    }
    all_ok = all_ok and cfg_ok

    # 2. Freeze-manifest confirmatory config (alpha, B, N, trials, seed) + consistency with forecaster.
    freeze = _load(FREEZE)
    fc = freeze.get("config", {})
    freeze_cfg_ok = (
        fc.get("test_alpha") == 0.05
        and fc.get("basin_tail") == 0.1
        and fc.get("primary_horizon_h_star") == 2
        and fc.get("b_permutation_confirmatory") == 10000
        and fc.get("n_subjects") == 20
        and fc.get("trials_per_subject") == 24
        and fc.get("randomization_seed") == 20260917
        and fc.get("basin_tail") == cfg.get("basin_tail")
        and fc.get("primary_horizon_h_star") == cfg.get("primary_horizon_h_star")
    )
    checks["freeze_confirmatory_config"] = {
        "pass": bool(freeze_cfg_ok),
        "test_alpha": fc.get("test_alpha"),
        "basin_tail": fc.get("basin_tail"),
        "h_star": fc.get("primary_horizon_h_star"),
        "B_permutation": fc.get("b_permutation_confirmatory"),
        "N_subjects": fc.get("n_subjects"),
        "trials_per_subject": fc.get("trials_per_subject"),
        "randomization_seed": fc.get("randomization_seed"),
    }
    all_ok = all_ok and freeze_cfg_ok

    # 3. Freeze-manifest code SHAs match on-disk files.
    code = freeze.get("code", {})
    sha_mismatches = []
    for rel, meta in code.items():
        p = ROOT / rel
        expected = meta.get("sha256")
        if not p.exists():
            sha_mismatches.append(f"missing: {rel}")
        elif expected and _sha256(p) != expected:
            sha_mismatches.append(f"changed: {rel}")
    code_ok = not sha_mismatches
    checks["freeze_code_shas"] = {
        "pass": bool(code_ok),
        "n_code_files": len(code),
        "mismatches": sha_mismatches,
        "predicted_basin_sha": code.get("src/causal_mind/causal/predicted_basin.py", {}).get("sha256", "")[:16],
    }
    all_ok = all_ok and code_ok

    # 4. Randomization manifest present and well-formed (seed, N, trials, per-subject sequences).
    rand = _load(RAND)
    manifests = rand.get("manifests", {})
    n_manifests = len(manifests)
    trials_ok = all(len(v) == rand.get("trials_per_subject") for v in manifests.values())
    rand_ok = (
        rand.get("seed") == 20260917
        and rand.get("n_subjects") == 20
        and rand.get("trials_per_subject") == 24
        and n_manifests == 20
        and trials_ok
        and rand.get("seed") == fc.get("randomization_seed")
    )
    checks["randomization_manifest"] = {
        "pass": bool(rand_ok),
        "seed": rand.get("seed"),
        "n_subjects": rand.get("n_subjects"),
        "trials_per_subject": rand.get("trials_per_subject"),
        "n_manifests": n_manifests,
        "all_trials_len_ok": bool(trials_ok),
        "scheme": rand.get("scheme"),
    }
    all_ok = all_ok and rand_ok

    # 4. Config + freeze + randomization SHAs match the frozen artifact registry.
    reg = _load(REGISTRY)
    reg_items = reg.get("artifacts", reg if isinstance(reg, list) else [])
    reg_map = {a.get("path"): a.get("sha256") for a in reg_items if isinstance(a, dict)}
    reg_mismatches = []
    for rel, label in [
        ("artifacts/cm8_forecaster/config.json", "config"),
        ("docs/ethics/cm8_software_freeze_manifest.json", "freeze"),
        ("data/manifests/cm8_randomization_manifest.json", "randomization"),
    ]:
        expected = reg_map.get(rel)
        actual = _sha256(ROOT / rel)
        if expected is None:
            reg_mismatches.append(f"not in registry: {label}")
        elif expected != actual:
            reg_mismatches.append(f"registry mismatch: {label}")
    reg_ok = not reg_mismatches
    checks["registry_shas"] = {
        "pass": bool(reg_ok),
        "mismatches": reg_mismatches,
        "config_sha": _sha256(CFG)[:16],
        "freeze_sha": _sha256(FREEZE)[:16],
        "randomization_sha": _sha256(RAND)[:16],
    }
    all_ok = all_ok and reg_ok

    # 5. No real human-data collection enabled pre-ethics.
    # The freeze manifest / config must not enable a real human-data pipeline.
    human_ok = not (cfg.get("human_data_enabled") or freeze.get("human_data_enabled"))
    checks["no_real_human_data"] = {"pass": bool(human_ok), "note": "synthetic pseudonyms only pre-ethics"}
    all_ok = all_ok and human_ok

    results = {
        "protocol": "CM-LAB S83 CM-8 confirmatory no-drift verification",
        "checks": checks,
        "decision": "CM8_CONFIRMATORY_INTACT" if all_ok else "CM8_DRIFT_DETECTED",
        "runtime_s": round(time.time() - t0, 2),
    }
    (OUT / "cm8_no_drift.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for k, v in checks.items():
        print(f"  [{'PASS' if v['pass'] else 'FAIL'}] {k}")
    print(f"[cm8] DECISION: {results['decision']}")
    print(f"[cm8] wrote {OUT / 'cm8_no_drift.json'} in {results['runtime_s']}s")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
