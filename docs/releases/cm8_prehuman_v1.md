# CM-8 Pre-Human Release v1.0

**Formal pre-human research freeze** of the CAUSAL MIND program, created from the
authoritative state before any human data collection.

## Freeze identity

- **Git SHA:** `8a9d5dd00c0d62ab6ba18e7a3ae28fbc74a85e14`
- **Tag:** `cm8-prehuman-v1.0`
- **Date:** 2026-09-20
- **Remote:** GitHub `main` = `8a9d5dd` (verified on the remote)
- **Working tree:** clean (no uncommitted scientific artifacts)

## Pre-freeze verification (all PASS)

- Working tree clean (only a scratch commit-message file, gitignored).
- Remote/main exact (pod = clone = GitHub main = `8a9d5dd`).
- All critical reports committed (CM-8R validation reports, CM-9A oracle lab).
- No credentials in tracked files (scan: 9 hits, all false positives — descriptions,
  `get-token` commands, and test fixtures for the credential scanner; no real secrets).
- No NEW participant data (no human data collected; the only tracked thought data is the
  PUBLIC OSF a56rm transcripts, 119 files / 3.2 MB, required for reproducibility).
- No large raw datasets accidentally tracked (no tracked file > 500 KB; the 28 MB forecaster
  weights are gitignored, SHA-verified).
- All manifest hashes valid (clean-room re-fit is bit-identical to the frozen forecaster).

## Completed phases

| Phase | State |
| --- | --- |
| CM-1 (data integrity) | `CM1_PASS` |
| CM-2 (next-thought prediction) | `CM2_PASS` |
| CM-3 (multi-horizon forecasting) | `CM3_PASS` |
| CM-5 (neural incremental value) | `CM5_NULL` (clean null) |
| CM-6 (causal identification) | `CM6_OBSERVATIONAL_ONLY_NO_IDENTIFICATION` |
| CM-7 (public intervention method validation) | `CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT` (method validated) |
| CM-8 (Pre-Oracle / Break-the-Chain) | `CM8_ETHICS_PACKAGE_READY` |
| CM-8R (pre-human hardening) | `CM8R_PREHUMAN_HARDENED` (10/10 gates) |
| CM-9A (synthetic Oracle lab) | `CM9A_SYNTHETIC_ORACLE_READY` |

## Scientific decisions (frozen)

- The CM-8 confirmatory protocol v1.0 is FROZEN: primary endpoint = BRP at h*=2; 4
  conditions (CONTROL/SHAM/GENERAL/CUE); basin tail 0.10; α=0.05 two-sided; B=10,000;
  N=20, 24 trials; seed 20260917; fixed counterbalanced randomization; ATE_GENERAL and
  ATE_CUE vs pooled CONTROL/SHAM.
- The participant-facing forecaster is FROZEN (LinearMultiHorizon, k=3, α=100, horizons
  1-10); basin radius calibrated on the held-out VAL split.
- The CM-5 neural null and the CM-7 public-intervention null are ACCEPTED as valid
  negative results (not reopened for positive results).
- The CM-6 observational structure is NOT treated as causal (0/84 edges identifiable).

## Frozen components (artifacts + hashes)

| artifact | SHA-256 | bytes |
| --- | --- | --- |
| `artifacts/cm8_forecaster/config.json` | `dbcbe443b6b09a3a33b53cfc1e1f6179a804cb3cef2ee8991444a7089e0cbd6a` | 2940 |
| `artifacts/cm8_forecaster/ridge_weights.npz` | `7b13d52ce520d15793814d3a10b6269a21cc3d54e0e7dfce20d206fb2c0ed094` | 28340170 |
| `artifacts/cm8_forecasting_freeze_manifest.json` | `21bb0bb8c0789772ff47a5d3d1e6e17721088bd86f3b8fa2a5cfa4cce3e29b06` | 5874 |
| `data/manifests/cm8_randomization_manifest.json` | `c6bcd84d7603d0a8e88e3cfdb005cab2a291b9f95ad24d158d9f417e4436032d` | 7905 |
| `data/manifests/cm2_split_seal.json` | `6bac3b4c432bbc42bb5a6ff95e2e5abaa47b5b5cd90e80a15d2c947cea635bd4` | 2204 |

Frozen code (SHA-256, from the freeze manifest):
- `src/causal_mind/forecast/multihorizon_model.py` `f360887be9d4100ce4d9e80fab01731824579cd9b2adca01db740072784afebc`
- `src/causal_mind/thought/encode.py` `bfea5e7ab781e24485c6b9dba13e229c90074db535479035f05f1c07ae6ad659`
- `src/causal_mind/thought/state_v1.py` `fabf8d53ea209fd3cb4366fb2fee1f2dd1af7cf0daa45fe39c8ab125855d34e7`
- `src/causal_mind/thought/multihorizon.py` `06499d48fd8bce6d2abda206082ee2ddf60c77355b2d90b5f38ac80ec7e4ed9c`
- `src/causal_mind/data/osf_a56rm.py` `187ab81b38a1433f02baa9a0b3d40dc36da8c6e8b0120d66c7a31665525ed2a7`
- `src/causal_mind/eval/protocol.py` `e84a0bdd8b62e133157f1cdcd6fffcde09e05540f2303d22228640e8810e5159`
- `src/causal_mind/causal/predicted_basin.py` `9f8ccceda05d202cedd4b9da3b35631534d0fefa1462e44f18b524d2bb96f4af`

## Ethics status

- `CM8_ETHICS_PACKAGE_READY`: supervisor-ready University-of-Vienna ethics package
  (`docs/ethics/`); frozen protocol v1.0; participant information + consent; GDPR
  data-protection plan; risk assessment; recruitment readiness; debrief; final
  preregistration; software-freeze manifest; dry run ALL PASS (no human data).
- Submission authority: the supervisor / responsible study-law body submits (the
  researcher prepares, does NOT submit).

## Human blockers (the ONLY remaining blockers to human data)

1. Supervisor / institutional sign-off.
2. Ethics approval (University of Vienna Ethics Committee).
3. Pilot authorization (CM-8P, gated).

No human data has been collected. The CM-8 confirmatory protocol is unchanged.

## Reproducibility commands

```bash
# on the pod, via SSH as jovyan
cd /home/jovyan/work/causal-mind-v2
export HF_HOME=/home/jovyan/work/.hf-home

# verify the frozen forecaster + clean-room reproduction (bit-identical)
.venv/bin/python data/scripts/cm8r_cleanroom.py

# verify the pre-human readiness scorecard (10/10 gates)
.venv/bin/python data/scripts/cm8r_readiness.py

# verify the participant-facing engine (offline, transactional)
.venv/bin/python data/scripts/cm8r_realtime_engine.py

# verify the synthetic Oracle lab
.venv/bin/python data/scripts/cm9a_oracle_lab.py

# full test suite + lint
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests scripts
```

## Provenance

- This release is a FORMAL FREEZE. Any change to the frozen components after this tag
  requires a new tag and a documented amendment. The frozen CM-8 confirmatory protocol
  (Workstream A) is immutable except for genuine reproducibility fixes.
