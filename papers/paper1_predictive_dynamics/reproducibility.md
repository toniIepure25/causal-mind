# Paper 1 — Reproducibility Statement

This statement maps every number in the Paper 1 manuscript to its exact source, so a
reviewer can reproduce each result from the frozen artifacts. Part of the
`cm8-prehuman-v1.0` freeze.

## Environment

- Pod: `/home/jovyan/work/causal-mind-v2`, Python via `.venv/bin/python`.
- Encoder: frozen `all-MiniLM-L6-v2` (local; `HF_HOME=/home/jovyan/work/.hf-home`).
- No network access is required at inference (frozen local artifacts).

## Data

- **Corpus:** OSF `a56rm` thought diaries (public). 118 subjects, 6,436 thought events.
- **Split:** subject-disjoint 83/18/17, **sealed** (seal `675052618750ea7f780c566230c47baabb983955b28bc35f49fe58d6c0408668`).
  The seal is in `data/manifests/cm2_split_seal.json` (SHA `6bac3b4c…`).
- **Representation:** frozen MiniLM embeddings; k≈3 history window.

## Frozen forecaster (the reproducibility anchor)

- `artifacts/cm8_forecaster/config.json` — SHA `dbcbe443…`
- `artifacts/cm8_forecaster/ridge_weights.npz` — SHA `7b13d52c…` (28 MB, gitignored)
- `artifacts/cm8_forecasting_freeze_manifest.json` — SHA `21bb0bb8…`
- **Clean-room guarantee:** a from-scratch re-fit from source + data is **bit-identical**
  to the frozen artifact (verified; `reports/cm8r_cleanroom/cm8r_cleanroom.json`).

## Number → source map

| manuscript claim | exact value | source |
| --- | --- | --- |
| next-thought semantic cosine | 0.3623 [0.3523, 0.3720] | `reports/cm2_results.json` → `main_model.test_sem_ci` |
| strongest baseline (B0) | 0.3167 [0.3078, 0.3250] | `reports/cm2_results.json` → `baselines.B0_marginal.semantic_ci` |
| permutation null | p=0.0000 | `reports/cm2_results.json` (CM-2 protocol) |
| h=1 gain | +0.0349 [0.0253, 0.0445] | `reports/cm3_results.json` → `FPC_semantic.1.gain` |
| h=2 gain | +0.0261 [0.0205, 0.0321] | `reports/cm3_results.json` → `FPC_semantic.2.gain` |
| h=3 gain | +0.0152 [0.0091, 0.0220] | `reports/cm3_results.json` → `FPC_semantic.3.gain` |
| h=4 gain | +0.0114 [0.0070, 0.0165] | `reports/cm3_results.json` → `FPC_semantic.4.gain` |
| h=5 gain | +0.0093 [0.0038, 0.0148] | `reports/cm3_results.json` → `FPC_semantic.5.gain` |
| h=10 gain | +0.0044 (CI excl. 0) | `reports/cm3_results.json` → `FPC_semantic.10.gain` |
| null robustness | p=0.0000 (time-shuffled / transition-destroyed / random-target) | CM-3 protocol (see `reports/cm3_results.json`) |
| BRP_control (basin calibration) | 0.0785 (target 0.10) | `reports/cm8r_ghost_pilot/cm8r_ghost_pilot.json` |

## Reproduction commands

```bash
cd /home/jovyan/work/causal-mind-v2
export HF_HOME=/home/jovyan/work/.hf-home

# verify the frozen forecaster + clean-room bit-identical re-fit
.venv/bin/python data/scripts/cm8r_cleanroom.py

# regenerate the CM-2 / CM-3 analyses from the frozen artifacts
.venv/bin/python data/scripts/cm8r_analysis.py

# full test suite + lint
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests scripts
```

## Guarantees

- **Deterministic:** fixed seeds (CM-2 seed 20260911; CM-3 same split/seal).
- **Sealed split:** no subject in more than one split; the seal is hash-verified.
- **Frozen model:** the forecaster is a frozen artifact; the clean-room re-fit is
  bit-identical.
- **No leakage:** subject-disjoint; no post-hoc tuning to the test split.
- **No overclaiming:** L3 (next-thought) and L5 (multi-horizon); no causal/free-will claim.
