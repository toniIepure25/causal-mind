# Claims Registry

Every claim made in this project (reports, README, papers) must appear here with a
level. Levels:

- **L0** pipeline sanity (code runs, formats parse, round-trips verified)
- **L1** association (variables co-vary; no causal language)
- **L2** out-of-sample prediction (subject-disjoint, above chance)
- **L3** incremental prediction beyond strong baselines (B0-B5)
- **L4** cross-subject generalization (repeated subject-level splits)
- **L5** temporal prospective prediction (future horizon, lag-audited)
- **L6** causal evidence from valid intervention / identification
- **L7** closed-loop trajectory redirection
- **L8** recursive prediction of attempted escape

Rules:

- Never word a lower-level result as a higher-level one.
- Never claim free will was proven or disproven.
- A claim's level can only be raised by a reviewer-approved gate pass, recorded here.

## Registered claims

| id | claim | level | evidence | status |
| --- | --- | --- | --- | --- |
| C-001 | Qwen endpoint + agent harness operate on the pod (pipeline sanity) | L0 | smoke tests 2026-09-09 | validated |
| C-002 | (reserved for first dataset-integrity result) | — | — | pending |
