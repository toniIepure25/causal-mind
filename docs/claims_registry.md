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
| C-002 | ds006067 dual-source dataset integrity (OpenNeuro MRI + OSF a56rm behavioral; 118 subjects; sentence transcripts 118, word-level 102, GPT ratings 118, human-validated 18; 10/10 cohort integrity checks) | L0 | CM-1 audit + CM-2 OSF pivot (2026-09-12) | validated |
| C-003 | Past thought history (k~3 window of frozen MiniLM text embeddings) predicts next-thought semantics above baselines B0-B7 (0.3623 vs 0.3265, non-overlapping CIs), out-of-sample, subject-disjoint (83/18/17 sealed), prospective; permutation p=0.0000; reproduced from a clean process. Effect modest; category arm unvalidated; NO causal claim. | L3 | CM-2 final report + red-team GO (2026-09-12) | validated |
| C-004 | Cognitive history (k~3 window of frozen MiniLM embeddings) predicts future thought semantics T[t+h] above the strongest frozen baseline at every event horizon h=1..10, with smooth monotonic decay of PredictiveGain (+0.0349 at h=1 to +0.0044 at h=10, all 95% CIs excluding 0); TPH_semantic >= 10 thoughts (~2 min, a lower bound); subject-disjoint (83/18/17 sealed), reproduced exactly; survives time-shuffled, transition-destroyed, and random-target nulls (p=0.0000). Effect modest; small test set (n=17); NO causal claim. | L5 | CM-3 final report + red-team GO (2026-09-13) | validated |
| C-005 | In the ds006067 think-aloud fMRI cohort (106 subjects, 73/17/16 subject-disjoint after pre-registered F2 tSNR + alignment gates), BOLD in the HRF-safe window [onset-21s, onset-6s] contains NO incremental predictive value for target-thought content beyond the frozen CM-3 behavioral-history model (k=3 MiniLM, alpha=100) plus 40 motion/speech nuisance regressors: IncrementalNeuralGain (M4-M2) is negative at every horizon h=1,3,5,10 (primary N2/Schaefer-400: -0.088/-0.085/-0.085/-0.090, 95% CIs excluding 0, 0/16 test subjects positive) and non-positive across the capacity ladder (N1 7-net ~-0.001, N3 PCA-50 ~-0.016, N2 400-parcel ~-0.085); NC4 (nuisance-only) -> 0; destructive controls NC1/2/3/5/6 confirm no hidden shortcut; robust to motion-screen sensitivity. Detection threshold ~0.005 (N1) / ~0.02 (N3) / ~0.11 (N2) cosine. A clean null: HRF-safe brain activity does NOT extend the behavioral predictive horizon for thought content in this task. NO causal/free-will claim; null is conditional on the frozen baseline, window, horizons, and dataset. | L5 | CM-5 decisive report + red-team GO (2026-09-14) | validated (negative result) |
