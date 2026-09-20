# CM-8R13 — Failure Injection (chaos)

- **State:** `CM8R_CHAOS_PASS`  | 7/7 faults handled loudly; logs parseable = True

| fault | handled | detail |
| --- | --- | --- |
| encoder_crash | PASS | marked INVALID_TECHNICAL, not analysis-valid |
| empty_thought | PASS | empty thought -> INVALID_TECHNICAL |
| prediction_failure | PASS | prediction failure -> INVALID_TECHNICAL |
| invalid_basin_radius | PASS | invalid basin -> INVALID_TECHNICAL |
| duplicate_finalization | PASS | duplicate finalization prevented |
| process_kill_resume | PASS | partial trial not logged (n_logged=0); session resumed |
| concurrent_write | PASS | concurrent write prevented (single writer) |

## Conclusion

The engine fails LOUDLY on all injected faults: no partial trial becomes analysis-valid, duplicate finalization and concurrent writes are prevented, the session resumes after a mid-trial kill, and all logs remain parseable JSONL. No silent data loss, no remote fallback.
