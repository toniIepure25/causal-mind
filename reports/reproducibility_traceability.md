# Reproducibility Traceability Table

Maps every reported result to its exact reproduction command, the frozen artifacts it
depends on, and the report it produces. Part of the `cm8-prehuman-v1.0` freeze. A reviewer
can reproduce any result by running the listed command on the pod.

## Environment (all results)

```bash
cd /home/jovyan/work/causal-mind-v2
export HF_HOME=/home/jovyan/work/.hf-home
.venv/bin/python ...
```

No network access is required at inference (frozen local artifacts).

## Result → reproduction map

| result | reproduction command | frozen artifacts / inputs | report produced |
| --- | --- | --- | --- |
| CM-2 next-thought prediction | `.venv/bin/python data/scripts/cm8r_analysis.py` | `artifacts/cm8_forecaster/` (SHA-verified); `data/manifests/cm2_split_seal.json` | `reports/cm2_results.json` |
| CM-3 multi-horizon | `.venv/bin/python data/scripts/cm8r_analysis.py` | same as CM-2 | `reports/cm3_results.json` |
| CM-5 neural null | `.venv/bin/python data/scripts/run_cm5.py` | CM-3 split projected onto MRI-eligible cohort; BOLD (gitignored, hash-verified) | `reports/cm5_decisive_results.json` |
| CM-6 identifiability | `.venv/bin/python data/scripts/run_cm6.py` | ds006067 thought stream (public) | `reports/cm6_observational_results.json` |
| CM-7 method validation | `.venv/bin/python data/scripts/cm7_analyze.py` | ds005494 (public, SHA manifest) | `reports/cm7_results.json` |
| CM-8R clean-room re-fit | `.venv/bin/python data/scripts/cm8r_cleanroom.py` | `artifacts/cm8_forecasting_freeze_manifest.json` | `reports/cm8r_cleanroom/cm8r_cleanroom.json` |
| CM-8R ghost pilot | `.venv/bin/python data/scripts/run_cm8r_ghost_pilot.py` | `artifacts/cm8_forecaster/`; ds006067 | `reports/cm8r_ghost_pilot/cm8r_ghost_pilot.json` |
| CM-8R Monte Carlo | `.venv/bin/python data/scripts/cm8r_monte_carlo.py` | `src/causal_mind/sim/` (21 scenarios) | `reports/cm8r_monte_carlo/cm8r_monte_carlo.json` |
| CM-8R power surface | `.venv/bin/python data/scripts/cm8r_power_surface.py` | `src/causal_mind/sim/` | `reports/cm8r_power_surface/cm8r_power_surface.json` |
| CM-8R BRP red team | `.venv/bin/python data/scripts/cm8r_brp_redteam.py` | `src/causal_mind/causal/predicted_basin.py` | `reports/cm8r_brp_redteam/cm8r_brp_redteam.json` |
| CM-8R basin robustness | `.venv/bin/python data/scripts/cm8r_basin_robustness.py` | `artifacts/cm8_forecaster/` | `reports/cm8r_basin_robustness/cm8r_basin_robustness.json` |
| CM-8R realtime engine | `.venv/bin/python data/scripts/cm8r_realtime_engine.py` | `src/causal_mind/engine/`; frozen artifacts | `reports/cm8r_realtime_engine/cm8r_realtime_engine.json` |
| CM-8R latency | `.venv/bin/python data/scripts/cm8r_latency.py` | `src/causal_mind/engine/` | `reports/cm8r_latency/cm8r_latency.json` |
| CM-8R chaos | `.venv/bin/python data/scripts/cm8r_failure_injection.py` | `src/causal_mind/engine/` | `reports/cm8r_failure_injection/cm8r_failure_injection.json` |
| CM-8R privacy | `.venv/bin/python data/scripts/cm8r_privacy.py` | `src/causal_mind/privacy/` | `reports/cm8r_privacy/cm8r_privacy.json` |
| CM-8R readiness (10/10) | `.venv/bin/python data/scripts/cm8r_readiness.py` | all CM-8R reports | `reports/cm8r_readiness/cm8r_readiness.json` |
| CM-9A Oracle lab | `.venv/bin/python data/scripts/cm9a_oracle_lab.py` | `src/causal_mind/oracle/` | `reports/cm9a_oracle_lab/cm9a_oracle_lab.json` |

## Frozen artifact hashes (the reproducibility anchor)

| artifact | SHA-256 |
| --- | --- |
| `artifacts/cm8_forecaster/config.json` | `dbcbe443b6b09a3a33b53cfc1e1f6179a804cb3cef2ee8991444a7089e0cbd6a` |
| `artifacts/cm8_forecaster/ridge_weights.npz` | `7b13d52ce520d15793814d3a10b6269a21cc3d54e0e7dfce20d206fb2c0ed094` |
| `artifacts/cm8_forecasting_freeze_manifest.json` | `21bb0bb8c0789772ff47a5d3d1e6e17721088bd86f3b8fa2a5cfa4cce3e29b06` |
| `data/manifests/cm8_randomization_manifest.json` | `c6bcd84d7603d0a8e88e3cfdb005cab2a291b9f95ad24d158d9f417e4436032d` |
| `data/manifests/cm2_split_seal.json` | `6bac3b4c432bbc42bb5a6ff95e2e5abaa47b5b5cd90e80a15d2c947cea635bd4` |

## Guarantees

- **Deterministic:** fixed seeds (CM-2/CM-3 seed 20260911; CM-8 seed 20260917).
- **Sealed splits:** subject-disjoint; seals hash-verified.
- **Frozen model:** the forecaster is a frozen artifact; the clean-room re-fit is
  bit-identical (SHA-verified).
- **No leakage:** subject-disjoint; no post-hoc tuning to test splits.
- **Offline inference:** no network at inference time.

## Full test suite + lint

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests scripts
```
