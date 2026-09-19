# CM-8B — BRP and the Predicted-Future Semantic Basin (formal definition)

- **Status:** DRAFT for red-team. Must be frozen (G1) before any confirmatory outcome.
- **Principle:** the basin is defined **prospectively** from (i) the frozen predictor and
  (ii) a held-out calibration of that predictor's error. It is NEVER tuned to the
  intervention outcomes.

## 1. Objects

- **Thought embedding:** each thought event `t` is encoded by the frozen MiniLM encoder to
  `e_t ∈ R^d` (d = 384).
- **Thought history:** `H_t = (e_{t-k}, …, e_{t-1})`, a window of the last `k` thoughts
  (k ≈ 3, as in CM-3).
- **Frozen predictor:** `f_θ : H_t → ŷ_t(h)`, the forecast of the semantic state `h` thought
  events ahead. `θ` is frozen (gate G8); it is NOT retrained on confirmatory outcomes.

## 2. Predicted-future basin (prospective geometric rule)

The predictor gives a point forecast `ŷ_t(h)`. To turn it into a *region* (a basin) we use
the predictor's own error, calibrated on held-out historical trajectories:

1. On a **held-out calibration set** (no intervention data), for each trial `i` compute the
   prediction-error norm `r_i = ‖ y_i(h) − f_θ(H_i)(h) ‖`.
2. The **prediction-interval radius** is `r_α = Quantile_{1−α}({r_i})` (primary: α = 0.10,
   i.e. the 90th percentile of the error norm).
3. The **predicted-future basin** at trial `t`, horizon `h` is the ball
   `B(t,h) = { z ∈ R^d : ‖ z − ŷ_t(h) ‖ ≤ r_α }`.

`r_α` is the radius within which the predictor *typically* lands; it is a property of the
predictor + the data, fixed before the experiment. This is a **prediction-interval basin**:
it is the high-probability region of the predicted future.

> Relationship to the CM-6 `SemanticBasin`: `SemanticBasin.fit(reference, quantile)` fits a
> ball around the reference centroid at a quantile of the reference distances. The
> CM-8 basin is the same object with the reference = the predicted-future distribution
> (centered at `ŷ_t(h)` with the held-out error spread). We implement it as
> `PredictedFutureBasin` so the radius is the *error* quantile, not an ad-hoc reference
> quantile.

## 3. Primary outcome — BRP

- **Basin distance (continuous):** `D(t,h) = ‖ e_{t+h} − ŷ_t(h) ‖ / r_α`. `D > 1` means the
  observed future is outside the predicted basin.
- **Leave indicator (binary):** `leave(t,h) = 1{ D(t,h) > 1 }`.
- **Branch Redirection Probability:** `BRP = P( leave(t,h) = 1 | intervention )`.

**Primary horizon `h*`** is frozen prospectively (chosen from the CM-3 predictive horizon +
pilot, NOT from outcomes). A primary at `h* ≥ 2` also serves the trivial-success guard
(below). The continuous `D(t,h*)` is the secondary (finer-grained) outcome for the ATE.

## 4. Causal estimands (primary)

- `ATE_GENERAL = E[ BRP | do(GENERAL REDIRECT) ] − E[ BRP | do(CONTROL/SHAM) ]`
- `ATE_CUE     = E[ BRP | do(SPECIFIC CUE) ]     − E[ BRP | do(CONTROL/SHAM) ]`

The reference arm (CONTROL/SHAM) is fixed in the preregistration. The primary ATE is NOT
conditioned on any post-treatment variable (no effort, no perceived success). Endogenous
(GENERAL) and exogenous (CUE) effects are estimated **separately** and not conflated.

## 5. Secondary outcomes (predefined)

- **Trajectory Divergence:** `‖ e_{t+h} − ŷ_t(h) ‖` (absolute) and vs a matched control
  future (the CM-6 `trajectory_divergence`).
- **Redirection Latency:** first `h` at which `leave(t,h) = 1` (thought events to first exit).
- **Redirection Persistence Horizon:** the largest `h` such that the trajectory remains
  redirected (outside the basin / in the new direction) for `h ≥ h*`; connects to the CM-3
  Thought Predictive Horizon.
- **Return Probability:** `P( re-enter B(t,h) after a leave )`.
- **Intervention Effect Decay:** per-horizon effect `e[h]` and its half-life (CM-6
  `intervention_effect_decay` / `trajectory_effect_over_horizon`).
- **Subjective Effort** and **Success Awareness:** self-report, analyzed **separately** from
  the objective trajectory outcomes (never in the primary ATE).

## 6. Trivial-success guard (SPECIFIC CUE)

A cue can "succeed" trivially if the participant just repeats the cue word (or an obvious
synonym). Guards, all frozen:
1. Primary horizon `h* ≥ 2` (not the immediate one-step echo).
2. **Cue-echo exclusion (semantic, not just lexical):** the persistence metric excludes
   thought events whose embedding is within a frozen cosine threshold of the cue embedding
   (this catches verbatim AND near-verbatim/synonym echoes, not just exact word repeats).
3. **Beyond-cue movement:** persistence requires the trajectory to enter the predefined
   **target basin** (a region in embedding space, not just the cue word) and stay there for
   the persistence horizon — i.e. movement into the target region that is not reducible to
   cue echoing.
4. **Cue-repetition baseline:** a control estimate of how often the cue is merely echoed
   without redirection (from the SHAM/neutral-cue data), used to set the echo threshold.

## 7. Freezing (gate G1)

Before confirmatory analysis, freeze and hash-seal:
- the predictor `θ` (G8) and its held-out calibration set;
- `α` (error quantile) and the resulting `r_α`;
- the primary horizon `h*`;
- the cue-echo lexical-overlap rule;
- the reference arm (CONTROL/SHAM).

Multiple basin metrics (e.g., ball vs k-NN radius, cosine vs Euclidean) may be compared
**during the pilot only**; exactly one is frozen for the confirmatory analysis.
