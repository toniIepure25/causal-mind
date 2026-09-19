"""Generate the CM-8 software freeze manifest (machine-readable SHAs/config hashes).

Freezes, before the human pilot: the baseline code (basin, estimator, power, dry-run,
randomization, primary analysis), the semantic encoder, the basin calibration, and the
randomization seed. The forecasting model SHA is a placeholder to be filled at the
pilot/confirmatory boundary (G8) — it is NOT retrained on confirmatory outcomes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path("/home/jovyan/work/causal-mind-v2")
OUT = ROOT / "docs" / "ethics" / "cm8_software_freeze_manifest.json"

# frozen code files -> role
CODE = {
    "src/causal_mind/causal/predicted_basin.py": "basin + BRP (semantic basin definition)",
    "data/scripts/cm8_synthetic.py": "estimator validation + primary ATE/permutation implementation",
    "data/scripts/cm8_power.py": "power analysis",
    "data/scripts/cm8_dry_run.py": "dry run + randomization manifest generator",
}

CONFIG = {
    "basin_tail": 0.10,          # BRP_control target (radius = 90th pct of held-out error norm)
    "primary_horizon_h_star": 2,  # frozen at preregistration seal (target)
    "test_alpha": 0.05,           # two-sided
    "b_permutation_confirmatory": 10000,
    "n_subjects": 20,
    "trials_per_subject": 24,
    "min_valid_trials_per_subject": 16,
    "reference_arm": "pooled CONTROL/SHAM (SHAM-alone sensitivity)",
    "randomization_seed": 20260917,
    "semantic_encoder": "sentence-transformers/all-MiniLM-L6-v2 (d=384, frozen)",
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _randomization_manifest(n_subjects: int, trials: int, seed: int) -> dict:
    """Counterbalanced per-subject condition manifest (round-robin, no consecutive runs)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    conds = ["control", "sham", "general", "cue"]
    per = trials // 4
    manifests = {}
    for s in range(n_subjects):
        base = conds[:]
        rng.shuffle(base)
        manifests[f"P-{s + 1:03d}"] = (base * (per + 1))[:trials]
    return {"seed": seed, "n_subjects": n_subjects, "trials_per_subject": trials,
            "scheme": "within-subject round-robin (no consecutive same-condition)",
            "manifests": manifests}


def main() -> None:
    files = {}
    for rel, role in CODE.items():
        p = ROOT / rel
        files[rel] = {"sha256": sha256(p), "bytes": p.stat().st_size, "role": role}
    # generate + freeze the randomization manifest
    rm = _randomization_manifest(CONFIG["n_subjects"], CONFIG["trials_per_subject"],
                                 CONFIG["randomization_seed"])
    rm_path = ROOT / "data" / "manifests" / "cm8_randomization_manifest.json"
    rm_path.parent.mkdir(parents=True, exist_ok=True)
    rm_path.write_text(json.dumps(rm, indent=2))
    files["data/manifests/cm8_randomization_manifest.json"] = {
        "sha256": sha256(rm_path), "bytes": rm_path.stat().st_size,
        "role": "frozen per-subject condition manifest"}
    manifest = {
        "experiment": "CM-8 (Pre-Oracle / Break the Chain)",
        "frozen_utc": None,
        "note": ("Forecasting model SHA is a placeholder to be filled at the "
                 "pilot/confirmatory boundary (G8); it is NOT retrained on confirmatory "
                 "outcomes. No human data is included in this manifest."),
        "code": files,
        "config": CONFIG,
        "forecasting_model": {
            "sha256": "HUMAN_INPUT_REQUIRED_AT_PILOT (G8 freeze)",
            "note": "CM-3-style predictor fit on historical/pilot data; frozen before confirmatory.",
        },
        "randomization_manifest": "data/manifests/cm8_randomization_manifest.json (generated at seal)",
    }
    import datetime
    manifest["frozen_utc"] = datetime.datetime.utcnow().isoformat() + "Z"
    OUT.write_text(json.dumps(manifest, indent=2))
    print(f"wrote {OUT}")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
