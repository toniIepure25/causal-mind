# CM-8R Publication Plan — Paper 1, Paper 2, Novelty Matrix

Pre-human (no human data). These are OUTLINES for the eventual publications; the CM-8
confirmatory results (the ATE) are NOT yet available (they require the human pilot +
confirmatory run). The outlines are based on the validated pre-human components.

## Paper 1 — "Predicting the Drift: Multi-Horizon Forecasting of First-Person Thought
Streams" (CM-2 + CM-3 + CM-5)

Contribution: a validated, reproducible pipeline for forecasting first-person thought
streams from a frozen, local semantic encoder + a linear multi-horizon model.

Sections:
1. Introduction: the problem of predicting the near-future of a person's thought stream
   (the "drift"); why it matters (cognitive science, mental-health monitoring, the
   "Break the Chain" intervention).
2. Data: the OSF A56RM thought-capture dataset (118 subjects, ~5964 thoughts); the
   subject-disjoint split (83/18/17, seed 20260911, sealed).
3. Method:
   - Frozen MiniLM encoder (all-MiniLM-L6-v2, 384-d, L2-normalized) — local, offline,
     reproducible.
   - LinearMultiHorizon (one Ridge per horizon h=1..10, k=3 history, alpha=100).
   - The predicted future basin (center = predicted, radius = the 90th-percentile
     held-out prediction-error norm).
4. Results:
   - CM-2: the split seal + the baseline BRP_control (~0.08 on held-out TEST).
   - CM-3: the linear multi-horizon model vs baselines (linear >= GRU; the simplest
     validated architecture is preferred).
   - CM-5: the forecasting freeze (clean-room bit-identical reproduction).
5. Discussion: the implications for the "Break the Chain" intervention; the limitations
   (the linear model, the event-horizon, the single dataset).

Novelty: the first validated, reproducible, OFFLINE pipeline for forecasting first-person
thought streams (no LLM, no internet, frozen local artifacts).

## Paper 2 — "Break the Chain: Causal Inference for Thought-Redirection Interventions"
(CM-6 + CM-7)

Contribution: a causal-inference framework for evaluating thought-redirection
interventions, with a validated null result on a held-out dataset.

Sections:
1. Introduction: the "Break the Chain" hypothesis (a brief intervention can redirect the
   near-future of a thought stream); the causal question (does the intervention CAUSE a
   change in the predicted future basin?).
2. Method:
   - The BRP (Basin Retention Probability) as the primary outcome.
   - The 4-condition design (CONTROL/SHAM/GENERAL/CUE); the ATE (intervention vs pooled
     control/sham).
   - The subject-clustered permutation test (B=10,000, two-sided alpha=0.05).
   - The randomization (fixed counterbalanced permutation, repeated).
3. Results:
   - CM-6: the causal framework + the dry run (ALL PASS).
   - CM-7: the validated NULL on ds005494 (CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT) — a
     negative result, reported honestly.
4. Discussion: the implications of the null; the power analysis; the CM-8 confirmatory
   design (the pre-human hardened experiment).

Novelty: the first causal-inference framework for thought-redirection interventions, with
a validated null result and a pre-human hardened confirmatory design.

## Novelty Matrix

| Component | Existing work | CM-8R contribution | Novelty level |
| --- | --- | --- | --- |
| Thought-stream forecasting | Next-word prediction, topic models | Multi-horizon forecasting of first-person thought streams (event-horizon, not next-word) | High |
| Semantic encoder | LLMs (GPT, etc.) | FROZEN, local, OFFLINE MiniLM (no LLM, no internet) | High (for the offline requirement) |
| Predicted future basin | Prediction intervals (regression) | The predicted future basin (a geometric object in embedding space) + the BRP | High |
| Causal inference for interventions | RCTs, A/B tests | The 4-condition design + the subject-clustered permutation test + the ATE on the BRP | Medium-High |
| Randomization | Standard RCT randomization | The fixed counterbalanced permutation (repeated, deterministic, audited) | Medium |
| Privacy | Standard de-identification | The privacy-hardened pipeline (PII detection, pseudonymization, encryption at rest, no remote telemetry) | Medium |
| Realtime engine | Standard experiment apps | The OFFLINE, transactional, chaos-tested experiment engine (no Qwen, no LLM, no internet) | High (for the offline + transactional requirement) |
| Pre-human hardening | Standard pre-registration | The CM-8R pre-human hardening (ghost pilot, Monte Carlo, BRP red team, basin robustness, clean-room reproduction, privacy red team, chaos, readiness scorecard) | High |
| Synthetic Oracle lab | Agent-based models | The synthetic Oracle lab (4 conditions, 11 policies, RPR/PIE, computational irreducibility) | High (exploratory) |

## Summary

The CM-8R work contributes a validated, reproducible, OFFLINE pipeline for forecasting
first-person thought streams (Paper 1) and a causal-inference framework for
thought-redirection interventions (Paper 2), with a pre-human hardened confirmatory
design. The novelty is in the OFFLINE, reproducible, causal, and pre-human-hardened
aspects, not in any single component.
