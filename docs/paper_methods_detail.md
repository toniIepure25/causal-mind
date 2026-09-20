# Paper-Quality Methods Detail

A consolidated, paper-ready methods description covering the full pipeline. Part of the
`cm8-prehuman-v1.0` freeze. This is the "Methods" content for Papers 1–3, written to the
detail a reviewer expects.

## 1. Data

- **Thought-stream corpus (OSF `a56rm`):** 118 participants, 6,436 thought events, from a
  public think-aloud cognitive-diary study with concurrent fMRI. Each event has a sentence
  transcript, semantic/affect ratings, and timing.
- **Intervention-validation corpus (ds005494):** 20 participants, 26 sessions, 3,330
  pairs, from a public open-loop hippocampal/entorhinal stimulation study (CC0).
- **Splits:** all behavioral splits are **subject-disjoint** and **sealed** (no subject in
  more than one split; no random row splits on temporal data). CM-2/CM-3: 83/18/17
  (train/val/test), seal `67505261…`.

## 2. Thought-state representation

- **Encoder:** frozen `all-MiniLM-L6-v2` sentence transformer (local; no network at
  inference). Each thought is a fixed-dimensional embedding.
- **State:** a k≈3 sliding window of recent thought embeddings. History depth saturates at
  k≈3 (deeper windows do not improve held-out prediction).
- **Target:** the embedding of the future thought at horizon h (semantic arm). The category
  (non-semantic) arm is reported as unvalidated.

## 3. Forecaster

- **Model:** `LinearMultiHorizon` — ridge regression (α=100) from the k≈3 history state to
  each horizon's target embedding, with horizon-specific heads.
- **Fitting:** on the train split only; hyperparameters (k, α) selected on the val split.
- **Frozen artifact:** `artifacts/cm8_forecaster/` (config + 28 MB weights). A **clean-room
  re-fit** from source + data is **bit-identical** to the frozen artifact (SHA-verified),
  which is the reproducibility anchor.

## 4. Baselines (Paper 1)

Eight baselines (B0–B7): marginal (B0), previous-state (B1), Markov (B2), n-gram (B3),
semantic persistence/drift (B4), semantic nearest-neighbor (B5), participant history (B6),
history retrieval (B7). For each horizon, the model is compared against the **strongest**
horizon-specific baseline, and the **gain** (model − strongest baseline) is reported with a
95% CI.

## 5. Evaluation (Paper 1)

- **Metric:** cosine similarity between predicted and actual future-thought embeddings
  (semantic arm).
- **CIs:** subject-level bootstrap (the unit of inference is the subject, matching the
  subject-disjoint split).
- **Nulls:** permutation null for the next-thought result (p=0.0000); the multi-horizon
  result survives time-shuffled, transition-destroyed, and random-target nulls (p=0.0000).
- **TPH:** the Thought Predictive Horizon is the horizon at which the gain's CI crosses
  zero; here it is beyond h=10, so TPH_semantic ≥ ~10 thoughts (~2 min), a lower bound.

## 6. Causal method (Papers 2–3)

- **Counterfactual engine:** refuses to label a counterfactual as causal unless a
  randomized-evidence record exists (enforced in code).
- **Estimand (BRP):** P(observed future leaves the frozen predictor's predicted-future
  basin | intervention). The basin is a ball around the frozen forecast with radius = the
  held-out 90th-percentile prediction-error norm (prospective; calibrated on VAL, h*=2,
  r_α=0.9911; not tuned to outcomes).
- **ATE estimands:** ATE_GENERAL and ATE_CUE, each vs pooled CONTROL/SHAM (SHAM-alone
  sensitivity).
- **Inference:** subject-clustered permutation test, B=10,000, two-sided α=0.05 (separate
  from the basin tail 0.10); subject-level bootstrap CIs.
- **Method validation (CM-7):** on ds005494, the framework correctly identifies
  (experimentally_identified) and estimates a randomized causal effect (ATE −0.0386,
  2-phase perm p=0.0733, list CI [−0.079, 0.002]); integrity 3328/3330; leakage audit PASS;
  destructive controls NC1/NC2/NC4 ≈ 0.

## 7. Pre-human validation (CM-8R)

- **Ghost pilot:** prospective replay of ds006067 through the frozen forecaster;
  BRP_control held-out TEST = 0.0785 (target 0.10), 118 ghost participants, 5,964
  forecasts, 0 missing events.
- **Monte Carlo:** type-I under the null calibrated at α=0.05 (finite-B artifact ruled out
  by a B-check).
- **Realtime engine:** offline (no Qwen/LLM/internet), transactional (append-only JSONL,
  atomic finalization, no duplicate finalization), full trial lifecycle; total critical
  path p95 = 478 ms, cold first trial = 876 ms.
- **Chaos:** 7/7 injected faults handled loudly (no partial trial becomes analysis-valid).
- **Privacy:** 12/12 tests (PII detection/redaction, pseudonymization, encryption at rest,
  no remote telemetry).
- **BRP red team:** 7/9 adversarial cases produce a misleading high BRP; secondary
  diagnostics (cosine-direction, Mahalanobis, persistence, novelty) reveal the modes.

## 8. Randomization and blinding (CM-8)

- **Randomization:** fixed counterbalanced permutation, seed 20260917, deterministic
  (predictable by design; mitigation = blinding). Audited: perfect balance, max run 1.
- **Blinding:** analysis blinding + experimenter blinding.

## 9. Ethics and privacy (CM-8)

- University-of-Vienna ethics package (frozen protocol v1.0, participant information +
  consent, GDPR data-protection plan, risk assessment, debrief, prereg, software-freeze
  manifest, dry run ALL PASS).
- **Privacy-by-design:** no raw thought text leaves the machine; embeddings only;
  pseudonymized (salted hash, encrypted salt); encryption at rest; access audit; complete
  deletion; no remote LLM/telemetry.

## 10. Software and reproducibility

- Python; `.venv/bin/python`; frozen local artifacts; no network at inference.
- Full test suite + `ruff` clean.
- Every result is reproducible from a committed script + frozen artifact (see the
  reproducibility traceability table).
