"""Seal the CM-5 frozen protocol BEFORE any decisive neural outcome."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SEAL_PATH = Path("/home/jovyan/work/causal-mind-v2/data/manifests/cm5_protocol_seal.json")
CM2_SEAL = "675052618750ea7f780c566230c47baabb983955b28bc35f49fe58d6c0408668"

PROTOCOL = {
    "anchor_commit": "23d20f1",
    "cm2_split_seal": CM2_SEAL,
    "split": {"train": 83, "val": 18, "test": 17},
    "hrf_safe_buffer_s": 6.0,
    "neural_history_window_s": 15.0,
    "tr_s": 1.5,
    "primary_alignment": "C_lagged_neural_history_hrf_buffer",
    "alignments": ["A_strict_pre_target", "B_hrf_safe_buffer",
                   "C_lagged_neural_history", "D_deconvolution_secondary"],
    "neural_ladder": ["N0_nuisance_only", "N1_network", "N2_atlas",
                      "N3_train_pca", "N4_small_encoder"],
    "models": ["M0_behavioral", "M1_neural_only", "M2_behavior_nuisance",
               "M3_behavior_neural", "M4_behavior_nuisance_neural"],
    "decisive_contrast": "M4_minus_M2",
    "residual_test": "brain -> (true_future - behavioral_prediction)",
    "horizons": [1, 3, 5, 10],
    "negative_controls": ["NC1_subject_perm", "NC2_temporal_shift",
                          "NC3_block_perm", "NC4_nuisance_only",
                          "NC5_neural_randomize", "NC6_target_perm"],
    "gates": ["N0_access", "N1_alignment", "N2_prospective_safety",
              "N3_incremental_value", "N4_null_survival",
              "N5_cross_subject", "N6_red_team"],
}


def main() -> None:
    canon = json.dumps(PROTOCOL, sort_keys=True)
    h = hashlib.sha256(canon.encode()).hexdigest()
    SEAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEAL_PATH.write_text(json.dumps({"seal": h, "protocol": PROTOCOL}, indent=2))
    print("CM-5 protocol SEAL:", h)
    print("written to", SEAL_PATH)


if __name__ == "__main__":
    main()
