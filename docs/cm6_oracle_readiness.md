# CM-6I — Oracle Readiness Criteria

Generated: 2026-09-16 · Engine: ORCHESTRATOR (CM-6I).
Gates **THE ORACLE**: the experiment in which a participant is *shown a prediction of their
own near-future thought* and then asked to **veto** or **redirect** it, after which we test
whether the *attempt to escape the prediction* is itself predictable (Recursive Predictability
Recovery, hypothesis H6).

> **THE ORACLE is NOT authorized.** It is gated behind the six criteria below. Each criterion
> names the evidence that must exist (and where it lives) before the gate opens. This is a
> *readiness* document, not a result.

## Why a gate

THE ORACLE is the highest-risk inference in the project: it couples (a) a *prediction* of a
person's own mind with (b) an *intervention* on that mind and (c) a *recursive* claim about
predicting the escape. Every one of those is a place where a leakage, a demand characteristic,
or an uncalibrated metric could manufacture a false "agency" signal. The gate exists so that
no single step is interpreted before the others are validated. **A negative result at any
gate is a valid, reportable outcome and stops the chain.**

## The six readiness criteria

| # | Criterion | What "ready" means | Evidence / where | Status |
| --- | --- | --- | --- | --- |
| R1 | **Reliable individual-level prospective prediction** | The CM-3 model predicts the near-future basin *per participant* (not just population-average), with a stable, measured per-subject skill (e.g., per-subject BRP-baseline or cosine) above a frozen floor, on a held-out session. | CM-3 report + a per-subject skill table (to be produced) | **NOT MET** (CM-3 is population-level; per-subject reliability unmeasured) |
| R2 | **A validated semantic trajectory metric** | The CM-6D metrics (SemanticBasin, BRP, CTE, trajectory divergence) pass known-answer tests (a synthetic shift is detected; a no-op is not), and show acceptable **test-retest reliability** on repeated baseline sessions. | `src/causal_mind/causal/{metrics,basin}.py` + known-answer tests (done) + a test-retest study (to be run) | **PARTIAL** (known-answer tests pass; test-retest not yet run) |
| R3 | **At least one causal redirection intervention** | The CM-6H pre-Oracle experiment shows a *measurable, matched-control-calibrated* effect of a randomized redirection instruction on BRP (the first L6-grade result). | CM-6H experiment (designed, not run) + IRB | **NOT MET** (design only) |
| R4 | **Measurable divergence from the predicted trajectory** | BRP / trajectory divergence is measurable and *above the matched-control baseline* with a CI excluding the control, in at least one condition. | CM-6H primary analysis | **NOT MET** (depends on R3) |
| R5 | **Persistence beyond immediate one-step effects** | The intervention effect has a measurable decay half-life (CM-6D `intervention_effect_decay` / `trajectory_effect_over_horizon`) > 1 step, i.e., the redirection is not a single-thought blip. | CM-6H horizon analysis | **NOT MET** (depends on R3) |
| R6 | **Acceptable test-retest reliability** | The *whole* predict→measure pipeline (segmentation → prediction → basin → BRP) is stable across sessions for the same participants (ICC / correlation above a frozen floor). | a two-session reliability study (to be run) | **NOT MET** |

## Gate rule

THE ORACLE proceeds **only if R1–R6 are all MET** (each with its named evidence recorded in
`docs/claims_registry.md` and a passing reviewer leakage audit). If any criterion is not met,
the project stays at the current stage (pre-Oracle) and the unmet criterion is the next
experiment. **No criterion may be waived to reach THE ORACLE.**

## What THE ORACLE will test (once ready)

1. **Prediction reveal:** show the participant their predicted near-future thought/basin.
2. **Veto / REDIRECT:** instruct to avoid (VETO) or choose an alternative (REDIRECT) branch.
3. **Measure:** the REACTIVE redirection effect (CM-6G mechanism 3) — divergence from the
   *revealed* prediction, calibrated against the no-reveal conditions (CUE / ENDOGENOUS) from
   CM-6F.
4. **Recursive Predictability Recovery (H6):** is the *probability of resisting/redirecting*
   the revealed prediction itself predictable from the pre-reveal state? (This is the L8
   claim, and it is the only step that even gestures at the "escape prediction" question. It
   still makes **no free-will claim**.)

## Anti-HARKing / freeze

The six criteria, the gate rule, and THE ORACLE's design are **frozen as of commit f3348dc (CM-6 baseline)**.
THE ORACLE's conditions, metrics, and hypotheses may not be changed after seeing pre-Oracle
outcomes without a new ADR + research-log entry. A pre-Oracle null on R3/R4/R5 **stops** THE
ORACLE; it is not a reason to redesign THE ORACLE to force a positive.
