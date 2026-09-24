# CM-LAB Scientific Deep Dive — Result Cards (CM-LAB §77-82)

One-page cards for each deep-dive workstream. Each card: **question → method → result →
decision → claim → guardrail**. Full machine-readable reports under `reports/`.

---

## Card 1 — External-validation inference adjudication (§25-28)
- **Question:** Does the CM-XVAL-1 gain survive proper subject-level inference and a null family?
- **Method:** Paired bootstrap, sign test, subject permutation, hierarchical bootstrap; null family
  N0-N6 (across-subject, within-subject, circular shift, block shuffle, history-target mismatch,
  transition-destroyed, wrong-subject history).
- **Result:** Subject-level gain survives at ALL horizons (CI excludes 0, sign p≤0.006, subject
  perm p≤0.0015, d 0.36-0.55). N0/N5 (subject identity) REJECTED (p=0.0005); N1-N4, N6 (temporal/
  transition) NOT rejected (p>0.29).
- **Decision:** `CMXVAL_PARTIAL_REPLICATION` — the model beats the strongest baseline, but the
  gain is driven by **subject identity**, not temporal/transition structure.
- **Claim:** C-101 (revised, OLD/NEW/REASON/EVIDENCE/COMMIT).
- **Guardrail:** No result shopping; negative nulls reported.

## Card 2 — Uncertainty, calibration, selective prediction (§32-35)
- **Question:** Can the model know when it will be wrong?
- **Method:** 4 uncertainty sources (distance-from-manifold, local residual var, bootstrap
  disagreement, neighborhood dispersion) vs forecast error; calibration; selective prediction.
- **Result:** Weak monotonic positive (spearman 0.10-0.16, AUROC 0.54-0.57); bootstrap
  disagreement is ANTI-calibrated (spearman -0.106). Selective prediction beats random modestly.
- **Decision:** `CMUNC_WEAK` — confidence gating must NOT be used in human Oracle work.
- **Claim:** C-102.
- **Guardrail:** TRAIN-only fitting; no test tuning.

## Card 3 — Representation + metric robustness (§29-31)
- **Question:** Is the CM-2/CM-3 finding specific to MiniLM, or robust to representation/metric?
- **Method:** 4 representations (MiniLM, mpnet, TF-IDF, NMF) x 4 metrics (cosine, euclidean,
  correlation, rank), same frozen split.
- **Result:** Gain positive 4/4 representations but effect-size ratio 5.9x (semantic >>
  lexical/topic). Baseline ranking changes; rank metric favors the baseline.
- **Decision:** `CMREP_PARTIAL` — the finding is representation-dependent (semantic >> lexical).
- **Claim:** C-104.
- **Guardrail:** CM-2/CM-3 claims remain tied to the MiniLM representation.

## Card 4 — Personalization + reliability (§36-40)
- **Question:** Does per-subject personalization improve forecasting? Is it reliable?
- **Method:** 17 test subjects, strict EARLY→LATE chronology; P1 (intercept) and P3 (ridge)
  personalization; reliability across sessions.
- **Result:** Personalization HURTS (all gains negative, -0.07 to -0.16, CIs exclude 0, all 17
  subjects). Reliability weak (pearson 0.143).
- **Decision:** `CMPERS_NULL` — personalization actively hurts (session drift + small adaptation
  data).
- **Claim:** C-103.
- **Guardrail:** Strict chronology; negative result reported.

## Card 5 — Local dynamics of the semantic trajectory (§41,43-47)
- **Question:** What is the local structure of the measured semantic trajectory?
- **Method:** Entropy, local linearity, nonlinear residual test, effective dimension,
  dimension-vs-predictability, attractor-like structure (all TRAIN-only).
- **Result:** Linear prediction dominant (residual ACF 0.076; negligible nonlinear residual).
  Trajectory highly dynamic (velocity 0.734, entropy 0.675, no recurrence/dwell/persistence).
  Higher local entropy predicts worse forecasting (spearman 0.57). Low local intrinsic dim (12)
  but high global participation ratio (109).
- **Decision:** `CMDYN_LINEAR_PREDICTION_DOMINANT`.
- **Claim:** C-105.
- **Guardrail:** Descriptive only; no "thought is linear" claim; no attractor overclaim.

## Card 6 — Forecast error taxonomy + error prediction (§48-49)
- **Question:** What kind of errors are large, and can we predict them in advance?
- **Method:** Outcome-blind algorithmic taxonomy of top-quartile errors; pre-forecast error
  prediction (AUROC).
- **Result:** Dominant failure mode is NOVELTY (rare state enriched 1.58x, abrupt jump 1.09x);
  gradual drift / weak history / rep ambiguity never occur. Pre-forecast prediction weak (best
  AUROC 0.585, distance-from-manifold).
- **Decision:** `CMERR_WEAKLY_PREDICTABLE`.
- **Claim:** C-106.
- **Guardrail:** Categories algorithmic (not hand-labeled); pre-forecast only.

## Card 7 — Oracle selective prediction + recursion (§63-71)
- **Question:** Can the model be used as a selective oracle? Is it stable under recursion?
- **Method:** Selective prediction (accuracy vs coverage); recursive rollout L0-L3 (feed own
  prediction back); theory note (stability, fixed point, performative, PIE, RPR, oracle game,
  info-gain planner).
- **Result:** Modest selective oracle (top-10% confidence → +0.039). Recursive rollout UNSTABLE
  (L0 0.406 → L3 0.314, performative error 0.092).
- **Decision:** `CMORACLE_SELECTIVE_ONLY` — use selective + NON-recursive for CM-8P.
- **Claim:** C-107.
- **Guardrail:** PIE flagged as human-gated (deferred to CM-8P with ethics approval).

## Card 8 — Research standards + leakage scanner (§50-59)
- **Result:** All standards mapped to runnable tools; NEW data-leakage scanner (L1-L5) PASSES
  across all 7 deep-dive scripts.
- **Decision:** `CMLEAK_PASS` / `CMSTD_IN_PLACE`.

## Card 9 — Disaster recovery, second independent run (§60)
- **Result:** Fresh clone → bootstrap → validate → integrity, all green (12 frozen artifacts
  unchanged). Fixed a `safe.directory` fragility (temp HOME with `.gitconfig`).
- **Decision:** `CMLAB_DISASTER_RECOVERY_REPRODUCED`.

## Card 10 — CM-8 confirmatory no-drift (§83)
- **Result:** Forecaster config, freeze confirmatory config, code SHAs, randomization manifest,
  registry SHAs all intact; no real human-data collection.
- **Decision:** `CM8_CONFIRMATORY_INTACT`.

---

## Negative results (reported, not bent) — §79
- `CMPERS_NULL` (personalization hurts).
- `CMUNC_WEAK` (confidence gating unreliable).
- `CMERR_WEAKLY_PREDICTABLE` (error prediction weak).
- CM-XVAL-1 temporal/transition nulls NOT rejected (subject identity drives the gain).

These are results. They bound what the model can and cannot do before any human work.
