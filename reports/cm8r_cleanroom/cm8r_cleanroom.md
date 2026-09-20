# CM-8R26/27 — Clean-Room Reproduction + Artifact Hash Manifest

- **State:** `CM8R_REPRODUCIBILITY_PASS`

## Checks
- PASS — frozen_weights_sha_matches_manifest: True
- PASS — split_seal_verified: True
- PASS — cleanroom_refit_bit_identical: True
- PASS — cleanroom_max_coef_diff: 0.0
- PASS — cleanroom_max_intercept_diff: 0.0

## Artifact hash manifest (16 artifacts)
| artifact | sha256 | bytes |
| --- | --- | --- |
| artifacts/cm8_forecaster/config.json | `dbcbe443b6b09a3a…` | 2940 |
| artifacts/cm8_forecaster/ridge_weights.npz | `7b13d52ce520d157…` | 28340170 |
| artifacts/cm8_forecasting_freeze_manifest.json | `21bb0bb8c0789772…` | 5874 |
| data/manifests/cm8_randomization_manifest.json | `c6bcd84d7603d0a8…` | 7905 |
| data/manifests/cm2_split_seal.json | `6bac3b4c432bbc42…` | 2204 |
| reports/cm8r_basin_robustness/cm8r_basin_robustness.json | `212d05a5b3be2a3b…` | 2047 |
| reports/cm8r_brp_redteam/cm8r_brp_redteam.json | `d1f68e77156c897e…` | 6416 |
| reports/cm8r_failure_injection/cm8r_failure_injection.json | `cc4dc342c2265594…` | 1346 |
| reports/cm8r_ghost_pilot/cm8r_ghost_pilot.json | `89f2fd9059e45ce8…` | 2120 |
| reports/cm8r_latency/cm8r_latency.json | `0a77e4b254653288…` | 1350 |
| reports/cm8r_monte_carlo/cm8r_monte_carlo.json | `cea748727eec3370…` | 8513 |
| reports/cm8r_monte_carlo/type1_B_check.json | `92cecfbbc583bdac…` | 868 |
| reports/cm8r_power_surface/cm8r_power_surface.json | `580646db7809bae8…` | 37752 |
| reports/cm8r_privacy/cm8r_privacy.json | `79e92098b702f988…` | 2325 |
| reports/cm8r_randomization/cm8r_randomization.json | `6874dd42df8667fe…` | 2516 |
| reports/cm8r_realtime_engine/cm8r_realtime_engine.json | `406899f6aa67b313…` | 1328 |

## Conclusion

The frozen confirmatory artifacts are reproducible: the forecaster weights SHA matches the manifest, the split seal verifies, and a CLEAN-ROOM re-fit from source + data (same code path, same seed) is bit-identical to the frozen artifact. The artifact hash manifest is the reproducibility anchor for the confirmatory experiment.
