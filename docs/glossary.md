# Glossary

**Status:** canonical · Terms used across the repository, in plain language.

## Core concepts

- **Thought state (`Z`)** — the latent cognitive/thought state the project
  models. Represented by a frozen text encoder (e.g. all-MiniLM-L6-v2, 384-d)
  over the thought transcript.
- **Thought stream** — the ordered sequence of thought states for one subject.
- **Target object** — `p(Z_future | causal_history, brain_history,
  thought_history, context, interventions, revealed_predictions)`: the
  distribution over future thought states given all available history.
- **Research program** — `OBSERVE → REPRESENT → FORECAST → EXPLAIN → INTERVENE
  → REDIRECT → PREDICT THE ESCAPE`.

## Prediction / evaluation

- **Horizon (`h`)** — how many thoughts ahead a prediction targets (h=1..10).
- **Primary horizon (`h*`)** — the headline horizon (CM-8: `h*=2`).
- **Semantic cosine** — cosine similarity between predicted and actual thought
  embeddings; the primary CM-2/CM-3 metric.
- **Baseline ladder (B0-B7)** — non-neural baselines a model must beat
  (marginal, persistence, Markov, k-history, drift, NN-trajectory, population
  avg, frozen-language history).
- **TPH** — "thoughts per horizon": the decision rule that a gain must hold over
  a minimum number of thoughts.
- **Null / negative control** — a control (time-shuffle, transition-destroyed,
  label-permutation) that should yield no effect; used to validate the method.
- **Permutation test** — destroys the temporal correspondence to build a null
  distribution for a p-value.

## Causality

- **SCM** — structural causal model.
- **Identifiability** — whether a causal effect can be determined from the
  observed data + assumptions (CM-6: 0/84 edges identifiable).
- **ATE** — average treatment effect.
- **Predicted basin** — a region in state space (center = prediction, radius =
  `r_alpha[h]`) used to define "staying on the predicted trajectory".
- **BRP** — "break-the-chain rate": fraction of post-intervention states outside
  the predicted basin at `h*`.
- **Counterfactual** — what would have happened under a different intervention.

## Oracle / intervention (CM-8 / CM-9A)

- **Oracle** — a (synthetic) agent that reveals a predicted future to the
  subject to test whether the prediction can be escaped.
- **RPR / PIE** — oracle-lab metrics (rate of predicted-escape / prediction
  intervention effect).
- **Selective prediction** — using the model only where it is confident
  (CM-8: helps only on the top-decile of samples).

## Repository / engineering

- **Frozen protocol / seal** — a protocol whose hash is persisted so it cannot
  be quietly changed (e.g. `cm2_split_seal.json`).
- **Frozen artifact** — a model/config whose SHA-256 is registered in
  `registries/artifact_registry.json`; immutable.
- **Claim (level 0-8)** — a checkable scientific statement registered at an
  explicit strength level in `claims/claims.json`.
- **Subject-disjoint split** — train/val/test split by subject (never random
  rows), so temporal data cannot leak across splits.
- **Leakage** — information from the test set (or the future) reaching a model
  or metric; the leakage scanner + reviewer audit guard against it.
- **Run ID** — a stable, traceable identifier for a run
  (`cm-<exp>-<UTCstamp>-<sha7>`), written into the output manifest.
- **Exit code contract** — stable, documented CLI exit codes
  (`src/causal_mind/exit_codes.py`); `0` = success.
- **Human-data guard** — the pre-commit/CI check that hard-fails if real
  participant data is staged before the human/ethics gate.
- **`cm` CLI** — the single operational entry point
  (`cm doctor`, `cm validate`, `cm reproduce`, …).

## Phases

- **CM-1…CM-9A** — the research program phases (data integrity → next-thought
  prediction → multi-horizon → neural → causal ID → intervention → oracle →
  synthetic oracle lab).
- **CM-8 / CM-8R** — the pre-Oracle / Break-the-Chain protocol and its
  pre-human hardening.
- **CM-LAB** — the scientific deep-dive phase (cross-validation, uncertainty,
  representation, personalization, dynamics, error prediction, oracle, leakage,
  disaster recovery).
