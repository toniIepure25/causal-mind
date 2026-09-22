# Uncertainty, Calibration, and Selective Prediction (CM-LAB §32-35)

**Decision:** `CMUNC_WEAK`
**Claim:** C-102 (new)
**Script:** `data/scripts/cm_uncertainty.py`
**Machine-readable:** `reports/cm_uncertainty/cm_uncertainty.json`
**Dataset:** ds006067 thought-stream (primary strong-signal regime), subject-disjoint
83/18/17, frozen CM-2 seal verified, seed 20260911, k=3, horizon h=1.
**Train samples:** 4308, **test samples:** 858, mean test error 0.6365.

---

## 1. Question (§32)

> Can the model know when it is likely to be wrong?

This is the prerequisite for an abstaining Oracle (§63): the Oracle should PREDICT or
ABSTAIN, not always emit a confident future. We build uncertainty estimates **without
changing CM-8** and test whether they track actual forecast error on held-out subjects.

## 2. Uncertainty sources (simple + interpretable first)

All estimates use **TRAIN statistics only** (no test-set tuning, no leakage). The model
is the frozen linear multi-horizon model fit on TRAIN.

| ID | Source | Definition |
|---|---|---|
| U1 | distance from training manifold | cosine distance of the history to its nearest TRAIN history |
| U2 | local residual variance | mean squared residual norm over the 20 nearest TRAIN histories |
| U3 | bootstrap disagreement | variance of 100 bootstrap-Ridge predictions for the history |
| U4 | neighborhood dispersion | mean pairwise cosine distance among the 20 nearest TRAIN targets |

## 3. Calibration (§33)

Error = `1 − cosine(prediction, actual target)`. Higher uncertainty should predict
higher error.

| Source | Spearman | Pearson | AUROC (large-error) | Decile err (low→high unc) | Monotonic? |
|---|---|---|---|---|---|
| U1 distance from manifold | **0.158** | 0.163 | **0.572** | 0.594 → 0.676 | yes |
| U2 local residual var | 0.103 | 0.099 | 0.538 | 0.613 → 0.656 | yes |
| U3 bootstrap disagreement | **−0.106** | −0.095 | **0.432** | 0.656 → 0.633 | **no (anti)** |
| U4 neighborhood dispersion | 0.135 | 0.132 | 0.562 | 0.605 → 0.657 | yes |

**Reading.**
- U1, U2, U4 show a **weak but real, monotonic** positive relationship with error
  (Spearman 0.10–0.16, AUROC 0.54–0.57). Being far from the training manifold, or in a
  semantically diffuse neighborhood, does predict somewhat higher error.
- **U3 (bootstrap disagreement) is anti-calibrated** (Spearman −0.106, AUROC 0.432):
  the model is *more* confident (less bootstrap spread) precisely when it is *more*
  wrong. The most "model-intrinsic" uncertainty source fails. This is a clear failure
  mode: the linear model's parameter uncertainty does not track its semantic error.
- Predictive-interval **coverage is not well-defined** for a single-embedding target
  (a point, not a scalar); the bootstrap 90% interval width is 0.0438 in cosine.
  Calibration is therefore assessed by rank correlation, AUROC, and decile monotonicity.

## 4. Selective prediction (§34)

Coverage-risk curves (confidence = −normalized uncertainty; keep top-f confidence).
Compared against random abstention at the same coverage.

| coverage | U1 mean error | random mean error |
|---|---|---|
| 0.10 | **0.5936** | 0.6329 |
| 0.30 | 0.6208 | 0.6480 |
| 0.50 | 0.6263 | 0.6394 |
| 1.00 | 0.6365 | 0.6365 |

Abstaining on the least-confident samples **does** reduce error below random abstention
(e.g., at 10% coverage, 0.5936 vs 0.6329, a ~0.04 reduction). But the benefit is modest
and the curve is flat in the mid-range: the uncertainty is too weak to support aggressive
abstention.

## 5. Decision (§35)

> **`CMUNC_WEAK`** — a weak, monotonic relationship between uncertainty and error exists
> (U1/U2/U4), and selective prediction beats random abstention modestly, but the
> relationship is **not operationally useful** for reliable abstention (AUROC ~0.57), and
> the model-intrinsic bootstrap disagreement is **anti-calibrated**.

**Consequence for the Oracle (§63):** per the §35 guardrail, confidence gating must NOT
be used in human Oracle work unless it reaches a defensible calibration state. It does
not. The synthetic Oracle confidence gate (§63) should therefore be expected to show
little or no reliability benefit from abstention, and the default policy should remain
**always-reveal (O-A)** unless a stronger uncertainty signal is found. This is a
legitimate, informative negative result: it bounds what the current model can support.

## 6. Guardrails

- No test-set tuning; all uncertainty from TRAIN only.
- No CM-8 change; no human data.
- The anti-calibrated U3 is reported, not hidden (negative-result policy §79).
