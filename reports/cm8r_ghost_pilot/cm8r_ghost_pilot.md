# CM-8R1 — Ghost Pilot on ds006067 (prospective replay, NOT causal)

- **State:** `CM8R_GHOST_PILOT_PASS`
- **Ghost participants:** 118 | **forecasts:** 5964 | h*=2 k=3 r_alpha=0.9911
- **BRP_control** (natural futures outside the frozen basin): held-out TEST = 0.0785, all subjects = 0.0439, target basin_tail = 0.1. A value near the target confirms the basin, calibrated on VAL, generalizes to the natural trajectory.
- **Forecast reproducibility:** online == batch, max diff 0.00e+00.
- **Deterministic replay:** identical = True.
- **Crash recovery:** ok = True (crash at event 18, resumed, identical).
- **Prediction latency (ms):** {'50': 0.196920707821846, '90': 0.21055657416582108, '95': 0.21580597385764122, '99': 0.2663338929414749, 'max': 21.778011694550514}
- **Missing events (total):** 0

## Checks
- PASS — brp_control_test_near_basin_tail
- PASS — forecast_reproducible
- PASS — deterministic_replay
- PASS — crash_recovery
- PASS — latency_p95_ms_below_100
- PASS — audit_log_written
- PASS — all_forecasts_computed

This is an ENGINEERING validation of the online pipeline (online construction, reproducibility, basin behavior, timing, storage, logging, latency, missing events, crash recovery, determinism). It is NOT a causal analysis and makes no treatment-effect claim.
