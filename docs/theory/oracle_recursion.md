# Oracle Recursion, Stability, and Performative Prediction (CM-LAB §65-71)

**Companion to:** `reports/cm_oracle/cm_oracle.json` (empirical §63-64)
**Status:** theory note (no new empirical claim; frames the §63-64 result)

This note formalizes the questions raised by the empirical Oracle result
(`CMORACLE_SELECTIVE_ONLY`): the model is a modest selective oracle but is **unstable under
recursive rollout** (L0→L3 accuracy drops 0.406→0.314). We frame the relevant concepts and
state what would be required to turn the model into a stable recursive oracle.

---

## §65 Stability of the recursive map

Let `f` be the one-step forecast map (history window → next embedding) and let the recursive
rollout be `x_{t+1} = f(x_t, x_{t-1}, ..., x_{t-k+1})` where each `x` is either the measured
state or the model's own prediction. The rollout is **stable** if small perturbations in the
seed history do not grow; it is **unstable** if they do.

Our empirical result (L0→L3 degradation 0.092) indicates the map is **contractive in the
measured direction but not in the prediction-residual direction**: replacing a measured entry
with a prediction injects a residual that the next `f` does not correct, and the residual
compounds. A direct-horizon ridge map has no mechanism to "re-anchor" to the measured
trajectory, so self-predictions drift.

**Stability condition (sufficient).** If `f` were a contraction in the embedding metric with
constant `< 1` on the reachable set, recursive rollout would converge to a fixed point and error
would not accumulate. Our ridge map is **not** such a contraction on the prediction-residual
subspace (empirically).

## §66 Fixed point

A **fixed point** of the recursive map is a trajectory `x*` such that `f(x*) = x*` (the model
predicts its own prediction). If the rollout converged, it would converge to a fixed point of
`f`. Our result shows the rollout does **not** converge to the measured trajectory; instead the
self-predicted trajectory drifts toward a region of the embedding space where the model is
confident (near the training manifold) but not where the subject actually is. This is the
"regression-to-the-manifold" failure: self-predictions are pulled toward the centroid of the
training manifold, losing subject-specific and time-specific information.

## §67 Performative prediction

**Performative prediction** (perdomo et al.) studies the fixed point of a model that is
retrained on its own predictions. Our setup is a lighter version: the model is **not**
retrained, but its predictions are used as **inputs**. The relevant object is the **performative
error** — the gap between the error on measured data and the error on self-predicted data. Our
empirical performative error is **0.092** (L0→L3), which is large relative to the base accuracy
(0.406). This is a **performative instability**: the model is not robust to its own outputs as
inputs.

## §68 Prediction–Intervention Equivalence (PIE)

PIE asks whether *predicting* a state is equivalent to *intervening* to produce it. For a
selective oracle, the distinction matters: presenting a forecast to a human is an **intervention**
on the human's subsequent thought (the human may conform to or resist the forecast). Our
empirical work does **not** test PIE (no human in the loop); it only tests the model's
self-consistency. PIE is a **human-gated** question and is deferred to the CM-8P pilot (with
ethics approval). We flag it here so the empirical result is not over-read as evidence about
human conformability.

## §69 Recursive Prediction Refinement (RPR) audit

RPR asks whether iterating the forecast (predict → use as input → predict again) **refines** the
forecast toward the truth. Our result is **negative**: iteration does not refine; it degrades
(L0→L3). The audit conclusion is that RPR is **not** a valid refinement procedure for this
model/representation. Any future RPR claim would require a contractive map or a re-anchoring
mechanism (e.g., blending self-predictions with the most recent measured state).

## §70 The oracle game

Frame the selective oracle as a **game** between the model (which chooses to forecast or abstain)
and the environment (which produces the next thought). The model's strategy is a **threshold on
confidence**; its payoff is accuracy on the forecasts it makes, minus a cost for abstention. The
empirical accuracy-vs-coverage curve (§63) is the **payoff curve** of this game. The optimal
strategy (maximizing payoff) depends on the abstention cost; at zero abstention cost the model
should forecast everything (full coverage), and at high abstention cost it should forecast only
the top-confidence events. The curve is **concave** (diminishing returns), so there is a well-
defined optimal coverage for any abstention cost. We report the curve so the abstention cost can
be set by the human protocol (CM-8P) rather than by the model.

## §71 Information-gain planner

An **information-gain planner** would choose, at each step, the action (forecast vs abstain vs
ask) that maximizes expected information gain about the next thought, subject to a budget. This
is a principled generalization of the selective oracle: instead of a fixed confidence threshold,
the planner balances the value of a forecast against the value of gathering more information
(e.g., waiting for the next measured state). We do **not** implement a full planner here; we
note that the §63 confidence and the §48-49 error-predictor are the building blocks (a scalar
value function over the pre-forecast state). A planner would require a model of the information
structure (how much the next measured state reveals), which is out of scope for this deep dive.

## Bottom line

- The model is a **modest selective oracle** (useful, concave payoff curve).
- It is **not a stable recursive oracle** (performative instability; RPR is negative).
- **PIE is human-gated** (deferred to CM-8P with ethics approval).
- A full **information-gain planner** is a future direction, not part of this deep dive.

**No CM-8 change. No human data. No result shopping.**
