# Oracle Selective Prediction + Recursive Depth (CM-LAB §63-64)

**Decision:** `CMORACLE_SELECTIVE_ONLY`
**Claim:** C-107 (new)
**Script:** `data/scripts/cm_oracle.py`
**Machine-readable:** `reports/cm_oracle/cm_oracle.json`
**Dataset:** ds006067 thought-stream, subject-disjoint 83/18/17, frozen CM-2 seal, seed 20260911, k=3, h=1.

**Scope.** §63 tests whether the model can be used as a **selective oracle** (predict only when
confident). §64 tests **recursive** prediction (feed the model's own prediction back as the next
history entry) and measures error accumulation. All fitting on TRAIN only.

---

## §63 Selective prediction (accuracy vs coverage)

| Coverage | Selected | Accuracy |
|---|---|---|
| full | 858 | 0.3635 |
| top 10% | 85 | **0.4029** |
| top 25% | 214 | 0.3900 |
| top 50% | 429 | 0.3787 |
| top 75% | 643 | 0.3731 |
| top 90% | 772 | 0.3684 |

Confidence = `1 − (nearest-neighbour cosine distance to the TRAIN history manifold)` (the best
pre-forecast uncertainty source from §32-35/§48-49). Selecting the **top-10% most confident**
forecasts raises accuracy from 0.364 to **0.403 (+0.039)**; the gain diminishes monotonically
with coverage. The selective oracle is **modestly useful** but not a strong effect.

## §64 Recursive depth (error accumulation)

| Depth | History composition | Accuracy |
|---|---|---|
| L0 | all-real | 0.4055 |
| L1 | 1 self-predicted | 0.3855 |
| L2 | 2 self-predicted | 0.3596 |
| L3 | 3 self-predicted | **0.3135** |

Feeding the model's own prediction back as the next history entry **degrades** accuracy by
**0.092** over 3 steps (L0→L3). The direct-horizon linear model is **not stable under
autoregressive rollout**: self-predictions drift out of the training distribution and accumulate
error. This is the empirical signature of the **performative / recursive instability** discussed
in the theory note (§65-71).

## Decision

> **`CMORACLE_SELECTIVE_ONLY`** — the model is a **modest selective oracle** (top-10%
> confidence → +0.039 accuracy) but is **NOT stable under recursive rollout** (L0→L3
> degradation 0.092). For the human Oracle work (CM-8P), the model should be used in a
> **selective, non-recursive** mode: present a forecast only when confident, and **never** feed
> the model's own prediction back as an input.

## Guardrails

- Confidence is pre-forecast only (distance to TRAIN manifold); no target leakage.
- Recursion uses the model's own predictions as inputs (the performative setup); no test tuning.
- All fitting on TRAIN only; no CM-8 change.
