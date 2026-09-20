# CAUSAL MIND — Technical Brief for the Supervisor

A deeper technical overview of the program, the frozen components, and the methods.
Companion to `cm_one_page.md`. All values are copied verbatim from the committed reports.
No human data; no CM-8 protocol changes.

## 1. The scientific program

The program has three linked workstreams:

1. **Forecast** — predict the next thought and future thought states from recent history.
2. **Explain** — characterize the (observational) thought dynamics and test what is
   causally identifiable.
3. **Intervene** — test, via a randomized experiment, whether a prediction-conditioned
   intervention causally redirects a predicted semantic trajectory.

The program moved from **FORECAST** (CM-2/CM-3) to **EXPLAIN** (CM-5/CM-6) to
**INTERVENE** (CM-7 method validation → CM-8 confirmatory design).

## 2. Data

- **ds006067 (OSF `a56rm` + OpenNeuro MRI):** 118 subjects, 6,436 thought events,
  sentence transcripts (118), word-level (102), GPT ratings (118), human-validated
  ratings (18). Cohort integrity 10/10. This is the thought-stream corpus.
- **ds005494 (OpenNeuro, CC0):** 20 subjects, 26 sessions, 3,330 pairs. A public
  semantic-priming / hippocampal-stimulation corpus used to **validate the causal
  method** (not the thought hypothesis).
- **Synthetic worlds:** `src/causal_mind/sim/` (21 scenarios S0–S20 with ground-truth
  causal parameters) and `src/causal_mind/oracle/` (the CM-9A synthetic Oracle lab).

All splits are **subject-disjoint** and **sealed** (no random row splits on temporal data).

## 3. The thought-state representation and forecaster

- **Encoder:** frozen `all-MiniLM-L6-v2` (local, no network at inference).
- **State:** a k≈3 sliding window of thought embeddings (history depth saturates at k≈3).
- **Forecaster:** `LinearMultiHorizon` (ridge, α=100), horizons 1–10. Fitted on the CM-2
  TRAIN split (83 subjects, seal verified). The **frozen artifact** is
  `artifacts/cm8_forecaster/` (config + 28 MB weights, SHA-verified; a clean-room re-fit
  from source + data is **bit-identical**).
- **Basin:** the predicted-future basin is a ball around the frozen forecast with radius =
  the held-out 90th-percentile prediction-error norm (prospective; calibrated on VAL,
  h*=2: r_α = 0.9911). Not tuned to outcomes.

## 4. Key results (exact values)

- **CM-2 (L3):** held-out semantic cosine **0.3623 [0.3523, 0.3720]** vs strongest
  baseline B0 **0.3167 [0.3078, 0.3250]**; permutation p=0.0000; 83/18/17 sealed.
- **CM-3 (L5):** gain over the strongest horizon-specific baseline: h=1 +0.0349
  [0.0253, 0.0445] → h=10 +0.0044 (all CIs exclude 0); smooth monotonic decay;
  TPH_semantic ≥ 10 thoughts (~2 min, a lower bound).
- **CM-5 (L5, null):** IncrementalNeuralGain (M4−M2) N2/Schaefer-400 = −0.088/−0.085/
  −0.085/−0.090 at h=1/3/5/10; 0/16 subjects positive; p=1.0; NC4→0; controls confirm.
- **CM-6 (L5, negative ID):** 124 candidate edges, 0 identifiable; analysis_7: 0/84
  identifiable (unmeasured confounding).
- **CM-7 (L6, method validated; null effect):** ATE −0.0386; 2-phase perm p=0.0733;
  list CI [−0.079, 0.002]; integrity 3328/3330 (99.94%); leakage PASS; destructive
  controls ~0.

## 5. The confirmatory experiment (CM-8) — frozen

- **Design:** within-subject, randomized, 4 conditions: CONTROL / SHAM / GENERAL-REDIRECT
  (endogenous) / SPECIFIC-CUE (exogenous).
- **Primary estimands:** ATE_GENERAL and ATE_CUE, each vs pooled CONTROL/SHAM (SHAM-alone
  sensitivity analysis).
- **Primary outcome:** BRP = P(observed future leaves the frozen predicted-future basin |
  intervention).
- **Inference:** subject-clustered permutation test, B=10,000, two-sided α=0.05 (separate
  from the basin tail 0.10).
- **Sample:** N=20, 24 trials, seed 20260917, fixed counterbalanced randomization.
- **Power:** N=20 is under-powered for small effects (documented on the power surface;
  power rises more with N than with trials; high ICC reduces power). Not changed.
- **Type-I audit:** at α=0.05 the empirical type-I error is 0.047 (MC 95% CI [0.013,
  0.080]), independently reproduced (alt-seed 0.040) → CALIBRATION PASS.

## 6. Pre-human hardening (CM-8R) — 10/10 gates

- **Ghost pilot:** BRP_control held-out TEST = 0.0785 (target 0.10), 118 ghost
  participants, 5,964 forecasts, 0 missing events.
- **Monte Carlo:** type-I under the null calibrated (finite-B artifact ruled out).
- **Realtime engine:** offline (no Qwen/LLM/internet), transactional (append-only JSONL,
  atomic finalization, no duplicate finalization), full trial lifecycle; total critical
  path p95 = 478 ms, cold first trial = 876 ms.
- **Chaos:** 7/7 injected faults handled loudly (no partial trial becomes analysis-valid).
- **Privacy:** 12/12 tests (PII detection/redaction, pseudonymization, encryption at rest,
  no remote telemetry).
- **Clean-room:** bit-identical re-fit (SHA-verified).
- **BRP red team:** 7/9 adversarial cases produce a misleading high BRP (magnitude-only,
  lexical echo, tiny-basin miscalibration, volatility); secondary diagnostics reveal the
  modes. BRP stays PRIMARY.

## 7. The synthetic Oracle lab (CM-9A)

A synthetic agent with a mean-reverting thought stream + an ORACLE that intervenes in 4
conditions (HIDDEN/REVEAL/VETO/REDIRECT) across 11 agent policies (O0–O10). Measures the
Relative Prediction Ratio (RPR) and Prediction–Intervention Effect (PIE). HIDDEN+O5 is
least predictable (RPR=1.48); VETO+O0 is most predictable (RPR=0.16). This is a synthetic
exploration (no claim about real human thought) and a separate research direction.

## 8. Reproducibility

Everything runs from frozen local artifacts; no network at inference. Exact commands in
`docs/releases/cm8_prehuman_v1.md`. Full test suite + `ruff` clean. The artifact hash
manifest is the reproducibility anchor.

## 9. Honest limitations

- Prediction effects are modest; the test set is small (n=17).
- The category (non-semantic) arm is unvalidated.
- The CM-7 effect is a null on a clinical iEEG population (no sham; retrieved, not free,
  semantic state).
- The CM-8 confirmatory run is **not yet done** (blocked on ethics + pilot).
- No free-will claim is made or implied anywhere.
