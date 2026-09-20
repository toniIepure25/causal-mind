# CM-8R10 — Realtime Engine (offline, transactional)

- **State:** `CM8R_REALTIME_ENGINE_PASS`  | subject P-001, 24 trials, h*=2 k=3 r_alpha=0.9911
- **Offline:** The engine uses ONLY frozen local artifacts (MiniLM encoder, ridge forecaster, basin radius, randomization manifest). No Qwen, no LLM API, no internet, no remote-agent orchestration.
- **Conditions (frozen manifest):** ['control', 'general', 'sham', 'cue', 'control', 'general', 'sham', 'cue', 'control', 'general', 'sham', 'cue', 'control', 'general', 'sham', 'cue', 'control', 'general', 'sham', 'cue', 'control', 'general', 'sham', 'cue']
- **BRP by trial:** [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

## Checks
- PASS — offline_no_remote_deps
- PASS — all_timestamps_ordered
- PASS — all_trials_finalized
- PASS — no_invalid_trials
- PASS — randomization_deterministic
- PASS — brp_computable_all
- PASS — lifecycle_integrity

## Lifecycle & timestamps
- Each trial follows CREATED -> BASELINE_CAPTURED -> PREDICTION_COMPUTED -> RANDOMIZED -> INTERVENTION_RENDERED -> POST_CAPTURED -> FINALIZED (or ABORTED / INVALID_TECHNICAL / WITHDRAWN). Analysis-valid only after atomic finalization; duplicate finalization is prevented.
- Every event is stamped with wall-clock UTC + monotonic local time; ordering is validated automatically.
