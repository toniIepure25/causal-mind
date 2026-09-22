# Local Dynamics of the Measured Semantic Trajectory (CM-LAB §41, §43-47)

**Decision:** `CMDYN_LINEAR_PREDICTION_DOMINANT`
**Claim:** C-105 (new)
**Script:** `data/scripts/cm_dynamics.py`
**Machine-readable:** `reports/cm_dynamics/cm_dynamics.json`
**Dataset:** ds006067 thought-stream, subject-disjoint 83/18/17, frozen CM-2 seal, seed 20260911, k=3, h=1.

**Scope.** The object of study is the *measured semantic trajectory in the frozen MiniLM
representation* — NOT a claim that "thought is linear." All fitting/tuning on TRAIN only.

---

## §41 Trajectory entropy

| Measure | Value |
|---|---|
| mean semantic velocity (consecutive cosine distance) | 0.7344 |
| mean local semantic entropy (NN dispersion) | 0.6748 |
| mean topic-switch rate | 1.00 |
| **local entropy vs forecast error (Spearman)** | **0.5745** |

The trajectory is **highly dynamic** (high velocity, high local entropy, near-constant topic
switching). And there is a **moderate positive correlation (0.57)** between local semantic
entropy and forecast error: **higher local entropy predicts worse forecasting.** This is a
descriptive/predictive result (not causal).

## §43 Local linearity

| Measure | Value |
|---|---|
| residual autocorrelation (lag 1) | 0.0758 |
| local curvature (mean) | 2.058 rad |

The linear model's **residual autocorrelation is small (0.076)**: the linear model captures
most of the temporal structure, leaving little predictable residual. The **trajectory
curvature is high (2.06 rad)** — but this is expected in a 384-dim space (consecutive points
point in different directions) and is a property of the *trajectory geometry*, not of the
*prediction*. It does **not** contradict the linear prediction.

## §44 Nonlinear residual test

| Measure | Value |
|---|---|
| k-NN residual cosine (train-only k-NN) | 0.0211 |
| random-residual null | −0.0026 |
| incremental nonlinear structure | marginal (0.021 vs −0.003) |

A small k-NN (fit on TRAIN) predicts the linear model's residuals only **marginally** above
the random-residual null (0.021 vs −0.003). The incremental nonlinear structure is
**negligible**: the linear model captures essentially all of the accessible predictive
structure. This is consistent with the CM-2/CM-3 finding that the linear model outperforms
the tested GRU.

## §45 Effective state-space dimension

| Measure | Value |
|---|---|
| PCA participation ratio | 108.79 |
| explained variance (top 10 / top 20) | 0.222 / 0.336 |
| MLE intrinsic dimension | 12.3 |
| ambient dimension | 384 |

The data has a **low local intrinsic dimension (~12)** but a **high global participation
ratio (~109)** — the signature of a low-dimensional manifold embedded in a high-dimensional
space. Predictive performance does **not** saturate in a very low-dimensional subspace
(top-20 PCA explains only 34%).

## §46 Dimension vs predictability (exploratory)

Dimension-vs-accuracy Spearman = **−0.087** (weak). The hypothesis "higher-dimensional / more
diffuse trajectories are less predictable" is **weakly** supported across subjects, not a
robust effect.

## §47 Attractor-like structure

| Measure | Value |
|---|---|
| mean recurrence fraction (cos > 0.8) | 0.0002 |
| mean dwell time | 1.001 |
| mean state persistence (lag-5 autocorr) | −0.0095 |

**No attractor-like structure**: the trajectory rarely returns to a similar state, does not
dwell, and does not persist. We do **not** call the embedding clusters "neural attractors";
the descriptive finding is that the measured semantic trajectory is highly transient.

## Decision

> **`CMDYN_LINEAR_PREDICTION_DOMINANT`** — the linear model captures most of the accessible
> predictive structure (small residual autocorrelation; negligible nonlinear residual),
> consistent with CM-2/CM-3. The measured semantic trajectory is **highly dynamic** (high
> velocity/entropy, high curvature, no recurrence/dwell/persistence), and **higher local
> entropy predicts worse forecasting** (Spearman 0.57). The local intrinsic dimension is low
> (~12) but the global participation ratio is high (~109). No attractor-like structure.

## Guardrails

- Descriptive/predictive only; no causal or "thought is linear" claim.
- All fitting/tuning on TRAIN only; no test-set tuning.
- No CM-8 change; no human data.
