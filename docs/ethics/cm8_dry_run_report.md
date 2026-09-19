# CM-8 Dry Run Report (synthetic + researcher-operated; NO human data)

- **Script:** `data/scripts/cm8_dry_run.py`. **Result:** ALL PASS.
- **Machine-readable results:** `reports/cm8_dryrun/dry_run_results.json`.
- **Purpose:** validate the platform plumbing (randomization, logging, timestamping,
  condition display, model latency, BRP computation, incomplete trials, participant abort,
  data export, pseudonymization) before the ethics-gated human pilot.

## Test results

| test | result | detail |
| --- | --- | --- |
| randomization | PASS | counterbalanced manifest; equal condition counts; no consecutive same-condition (round-robin) |
| condition display | PASS | the 4 conditions are distinct and non-empty |
| model latency | PASS | stand-in frozen predictor: mean 0.002 ms, max 0.04 ms (well within the inter-thought budget) |
| BRP computation | PASS | BRP_control = 0.088 (≈ target 0.10); a known push raises BRP to 1.0 |
| incomplete trial | PASS | a trial with < N_min (4) valid embeddings is excluded (pre-specified) |
| participant abort | PASS | a mid-session abort is handled (partial data, withdrawal flag, retention threshold) |
| data export | PASS | export uses the study code only; no identity in the data file; identity key stored separately |
| timestamping | PASS | high-resolution (ns) audit-log timestamps |

## Notes

- The **model latency** test uses a stand-in linear predictor (the real frozen MiniLM-based
  predictor is frozen at the pilot/confirmatory boundary, G8); the latency budget check
  confirms the pipeline can compute the forecast in realtime.
- The **BRP** test confirms the basin calibration (BRP_control ≈ 0.10) and that an
  intervention push raises BRP, on D-dimensional embeddings.
- The **data export / pseudonymization** test confirms the identity key is separate from the
  pseudonymized data (no identity leakage into analysis files).
- **No human data** was used or collected in this dry run.
