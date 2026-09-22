# Forecast Error Taxonomy + Error Prediction (CM-LAB §48-49)

**Decision:** `CMERR_WEAKLY_PREDICTABLE`
**Claim:** C-106 (new)
**Script:** `data/scripts/cm_error_taxonomy.py`
**Machine-readable:** `reports/cm_error_taxonomy/cm_error_taxonomy.json`
**Dataset:** ds006067 thought-stream, subject-disjoint 83/18/17, frozen CM-2 seal, seed 20260911, k=3, h=1.

**Scope.** §48 is an **outcome-blind, algorithmic** taxonomy of large forecast errors (top
quartile, err ≥ 0.702; 215/858 test samples). §49 uses **pre-forecast information only** to
predict whether the next forecast will be poor. All fitting on TRAIN only.

---

## §48 Error taxonomy (enrichment among large-error events)

| Category | All events | Large error | Enrichment |
|---|---|---|---|
| abrupt_jump (target far from history mean) | — | — | **1.09** |
| gradual_drift (target near history, prediction off) | — | — | 0.0 (never occurs) |
| high_local_entropy (diverse local neighborhood) | — | — | 0.998 (not enriched) |
| rare_state (target far from TRAINING manifold) | — | — | **1.58** |
| weak_history (very similar k history) | — | — | n/a (never occurs) |
| rep_ambiguity (prediction similar to many targets) | — | — | n/a (never occurs) |

**Interpretation.** Large errors are most associated with **rare states** (the actual next
thought is far from anything seen in training; enrichment 1.58) and **abrupt semantic jumps**
(the next thought departs sharply from the recent history; enrichment 1.09). High local
entropy is common across all events and is **not** specifically enriched among large errors.
Three categories (gradual drift, weak history, representation ambiguity) **never occur** in
this dataset — the linear model does not drift when the target is near the history, the
history is never low-variability, and predictions are specific. These absences are themselves
informative: the dominant failure mode is **novelty** (rare / abrupt), not model drift.

## §49 Error prediction (pre-forecast only)

| Predictor | AUROC (top-quartile error) |
|---|---|
| U1 distance-from-manifold | **0.5853** |
| U4 local entropy | 0.5606 |
| heuristic semantic volatility | 0.5183 |

The **distance-from-manifold** uncertainty source is the best (and only marginally useful)
predictor of large errors (AUROC 0.585). The simple heuristic (semantic volatility) is the
**worst** (0.518) — so we do **not** preserve a simple-heuristic win. All predictors are
**weak** (0.52–0.59), consistent with the §32-35 uncertainty finding (`CMUNC_WEAK`): the
model cannot reliably know in advance which forecasts will be poor.

## Decision

> **`CMERR_WEAKLY_PREDICTABLE`** — the dominant large-error mode is **novelty** (rare state,
> enrichment 1.58; abrupt jump, 1.09), not model drift (gradual drift never occurs). Pre-
> forecast error prediction is **weak** (best AUROC 0.585, distance-from-manifold); the simple
> semantic-volatility heuristic is worse (0.518). Consistent with `CMUNC_WEAK`.

## Guardrails

- §48 categories computed algorithmically (thresholds on cosine distances), not hand-labeled.
- §49 uses pre-forecast information only (no target leakage).
- All fitting on TRAIN only; no test-set tuning; no CM-8 change.
- Absent categories (gradual drift, weak history, rep ambiguity) reported as absent, not
  suppressed.
