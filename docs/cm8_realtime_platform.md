# CM-8C — Realtime Prediction + Intervention Platform (architecture)

- **Status:** DRAFT architecture. The outcome engine reuses `predicted_basin.py` +
  `causal_mind.causal.metrics`; the capture/UI layer is decided after the pilot modality.
- **Goal:** a platform that can run the CM-8 trial in realtime and, later, support the
  Oracle (CM-9). All timestamps high-resolution and auditable.

## Pipeline

```
Participant UI
  -> Thought capture            (think-aloud / typed / probes; modality frozen after pilot)
  -> ThoughtState encoder       (frozen MiniLM -> e_t in R^384; thought segmentation)
  -> Frozen future predictor    (f_theta: H_t -> y_hat_t(h); FROZEN, no retraining)
  -> Basin estimator            (PredictedFutureBasin: center=y_hat_t(h*), radius=r_alpha)
  -> Randomization engine       (frozen per-subject condition manifest; seed logged)
  -> Intervention renderer      (CONTROL / SHAM / GENERAL REDIRECT / SPECIFIC CUE)
  -> Post-intervention capture  (subsequent thought sequence)
  -> Outcome engine             (BRP, divergence, latency, persistence, return, decay)
  -> Audit log                  (every timestamp + decision, append-only)
```

## Components

- **Thought capture:** records the raw stream with per-thought onset/end timestamps. The
  modality (think-aloud vs typed vs probes) is a pilot decision; the platform is
  modality-agnostic (a capture adapter per modality).
- **ThoughtState encoder:** the frozen MiniLM encoder (same as CM-2/3/7). Thought
  segmentation (sentence/utterance boundary) is validated in the pilot.
- **Frozen future predictor:** the CM-3-style model, frozen (G8). Inference latency is
  logged; it must complete before the intervention is rendered (realtime constraint).
- **Basin estimator:** `PredictedFutureBasin` (center = forecast at `h*`, radius = `r_α`
  pre-calibrated on held-out data).
- **Randomization engine:** reads the frozen per-subject condition manifest (G3); logs the
  seed and the assigned condition per trial.
- **Intervention renderer:** presents the condition's instruction/cue with a logged
  presentation timestamp.
- **Outcome engine:** computes BRP (at `h*`), divergence, latency, persistence horizon,
  return probability, and effect decay from the post-intervention thought embeddings,
  using `predicted_basin.py` + `causal_mind.causal.metrics`.

## Audit log (append-only, per trial)

- thought onset / submission / end timestamps (high-resolution);
- model inference time (predictor latency);
- intervention presentation timestamp + condition;
- response timing;
- the prediction `y_hat_t(h*)` and the predicted basin (center, `r_α`);
- the actual subsequent states and the computed BRP / divergence / persistence.

## Realtime constraints

- The predictor + basin must be computed **before** the intervention is rendered (the
  participant's post-intervention stream is the outcome). Inference latency budget is set
  in the pilot (target: predictor completes within the inter-thought gap).
- No retraining or parameter update during the session (predictor frozen).

## What exists vs to-build

- **Exists (reuse):** frozen MiniLM encoder; `SemanticBasin` / `PredictedFutureBasin`;
  `branch_redirection_probability`, `trajectory_divergence`, `intervention_effect_decay`,
  `trajectory_effect_over_horizon`; the counterfactual engine.
- **To-build (CM-8C):** the capture adapters + UI, the thought-segmentation validator, the
  randomization engine + manifest, the intervention renderer, the outcome-engine driver,
  and the append-only audit log. These are built and validated in the pilot (CM-8P) before
  the confirmatory run (CM-8H).
