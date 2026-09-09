# ADR-002: Subject-disjoint evaluation protocol

Status: accepted (2026-09-09)

## Context

Temporal data with within-subject autocorrelation makes random row splits invalid
(neighbor leakage inflates skill).

## Decision

1. Splits are always subject-disjoint: each participant appears in exactly one of
   train/val/test.
2. Split definitions are generated with a fixed seed and stored in the experiment
   manifest; the final holdout (if size permits) is evaluated once per protocol
   version.
3. Repeated subject-level splits (>= 5, fixed seeds) are the default reporting unit;
   we report the distribution over splits, not a single split.
4. Automated integrity checks (in `causal_mind.utils.splits`) verify: no shared
   subjects, no temporal crossing, session-id uniqueness per subject, and duplicate
   transcript detection.
5. Session/run identity is never a model input; it is used only for integrity checks.

## Consequences

- Effective sample size is the number of subjects, not rows; power analysis must use
  subject-level effects.
- Any experiment that cannot be evaluated subject-disjoint is not run.
