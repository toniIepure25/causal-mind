"""Seal the CM-3 frozen protocol BEFORE any decisive multi-step outcome (CM-3A)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SEAL_PATH = Path("/home/jovyan/work/causal-mind-v2/data/manifests/cm3_protocol_seal.json")
CM2_SEAL = "675052618750ea7f780c566230c47baabb983955b28bc35f49fe58d6c0408668"

PROTOCOL = {
    "anchor_commit": "a0a701a",
    "cm2_split_seal": CM2_SEAL,
    "split": {"train": 83, "val": 18, "test": 17},
    "event_horizons": [1, 2, 3, 4, 5, 6, 8, 10],
    "time_horizons_s": [30, 60, 120, 180],
    "targets": ["semantic", "topic", "category", "psychological", "trajectory_direction"],
    "primary_model": "linear_multi_horizon_transition",
    "baselines": ["B0_marginal", "B1_persistence", "B2_markov_iterated", "B3_khistory",
                  "B4_drift", "B5_nn_trajectory", "B6_population_avg", "B7_frozen_lang_history",
                  "cm2_linear_transition"],
    "tph_rules": ["gain>0", "ci_excludes_0", "survives_null",
                  ">=60pct_subjects_above_baseline", "redteam_clean"],
    "nulls": ["time_shuffled", "transition_destroyed"],
}


def main() -> None:
    canon = json.dumps(PROTOCOL, sort_keys=True)
    h = hashlib.sha256(canon.encode()).hexdigest()
    SEAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEAL_PATH.write_text(json.dumps({"seal": h, "protocol": PROTOCOL}, indent=2))
    print("CM-3 protocol SEAL:", h)
    print("written to", SEAL_PATH)


if __name__ == "__main__":
    main()
