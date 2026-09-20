# From Prediction to Intervention: A Validated Causal-Inference Method for the Thought Stream, and a Frozen Confirmatory Design

**Manuscript draft (Paper 2 — prediction to intervention).** Status: pre-submission draft,
part of the `cm8-prehuman-v1.0` freeze. All values are copied verbatim from the committed
reports. No human data beyond public corpora; the confirmatory human experiment is **designed
and frozen but not yet run** (ethics-gated).

---

## Abstract

Predicting a future state is not the same as changing it. We address the gap between
*forecasting* the human thought stream and *intervening* on it in a causally identifiable
way. First, we show that the **observational** thought stream is **not** causally
identifiable: of 84 candidate lagged edges, **0** are identifiable (every backdoor-blocking
set requires an unobserved latent node), so no observational analysis can support a causal
claim. Second, we build and **validate** a causal-inference method (a counterfactual engine
that refuses to label an unidentified counterfactual as causal, a subject-clustered
permutation estimator, and a predicted-future-basin estimand) on an **independent public
dataset** (ds005494, N=20), where it correctly identifies and estimates a randomized causal
effect (ATE −0.039, two-phase permutation p=0.073 — a valid null; the *method* is the
result; leakage audit passed; destructive controls at zero). Third, we freeze a
**confirmatory** within-subject, randomized, four-condition experiment (CONTROL/SHAM/
GENERAL-REDIRECT/SPECIFIC-CUE) whose primary outcome is the probability the observed future
leaves the frozen predictor's predicted-future basin (BRP), and we pre-human harden it
(10/10 gates: frozen reproducible forecaster, offline transactional engine, audited
randomization, hardened privacy, clean-room bit-identical reproduction). The human run is
blocked only on ethics approval and a pilot. We make no free-will claim.

## 1. Introduction

A forecastable thought stream (Paper 1) raises a sharper question: can we **change** the
future thought state, and can we **estimate that change causally**? Three obstacles:
(1) the observational thought stream is confounded (no randomization), so observational
analyses cannot identify causal effects; (2) a causal method must be validated before it is
trusted on the real question; and (3) the confirmatory experiment must be frozen and
pre-validated before any human data, so that the analysis cannot be tuned to the outcome.
We address all three.

## 2. The identification problem (why the confirmatory step is randomized)

On the observational thought stream (118 subjects, 6,436 thoughts), we ran a full
identifiability audit (CM-6). **Result: 0 of 84 candidate lagged edges are causally
identifiable** — every backdoor-blocking set requires at least one unobserved node
(unmeasured confounding, including the per-subject rating baseline). The robust
observational signal (e.g., the linguistic-load cluster, duration→gap r_partial=0.828) is
reported as **candidate, not causal**. **Consequence:** the confirmatory test of
intervention must be a *randomized* experiment, not an observational analysis.

## 3. The causal method

- **Counterfactual engine:** refuses to label a counterfactual as causal unless a
  randomized-evidence record exists (enforced in code; raises otherwise).
- **Estimand:** the predicted-future-basin rate (BRP) — P(observed future leaves the frozen
  predictor's predicted-future basin | intervention) — and the ATE of each intervention vs
  pooled CONTROL/SHAM.
- **Inference:** subject-clustered permutation test (B=10,000, two-sided α=0.05);
  list/subject-level bootstrap CIs where applicable.
- **Machinery validation:** 61/61 tests pass; ruff clean.

## 4. Method validation on an independent public dataset (CM-7)

We validated the method on **ds005494** (Herrema & Kahana; N=20, 26 sessions, 3,330 pairs) —
an open-loop hippocampal/entorhinal stimulation study with list-level within-subject
randomization. The framework **correctly identified** (experimentally_identified) and
**estimated** a site-specific ATE of stimulation at encoding on subsequent cued recall:

- **ATE = −0.0386**; exact two-phase randomization **p = 0.0733** (20-subset robustness
  p=0.0754); list-level 95% CI **[−0.079, 0.002]**; subject-level [−0.087, 0.011].
- **Integrity:** 3328/3330 (99.94%); 0 x-precedes-y violations; 0 missing outcomes.
- **Leakage audit:** PASS (no post-treatment variable in the adjustment set; retrieval-stim
  excluded from the future-state estimand).
- **Destructive controls:** NC1/NC2/NC4 ≈ 0 (the machinery does not hallucinate effects).

**Interpretation:** the *specific effect* is a small, non-significant null (a valid null);
the *method* is validated as a causal-inference instrument. Caveats: clinical iEEG
population, no sham, retrieved (not free) semantic state, 14/26 sessions truncated (does not
bias the within-list ATE).

## 5. The frozen confirmatory design (CM-8)

- **Design:** within-subject, randomized, 4 conditions: CONTROL / SHAM / GENERAL-REDIRECT
  (endogenous) / SPECIFIC-CUE (exogenous).
- **Primary estimands:** ATE_GENERAL and ATE_CUE, each vs pooled CONTROL/SHAM (SHAM-alone
  sensitivity).
- **Primary outcome:** BRP (the predicted-future-basin rate).
- **Inference:** subject-clustered permutation, B=10,000, two-sided α=0.05 (separate from
  the basin tail 0.10).
- **Sample:** N=20, 24 trials, seed 20260917, fixed counterbalanced randomization.
- **Type-I audit:** empirical type-I at α=0.05 = 0.047 (MC 95% CI [0.013, 0.080]),
  independently reproduced (alt-seed 0.040) → CALIBRATION PASS.
- **Power:** N=20 is under-powered for small effects (documented; power rises more with N
  than trials; high ICC reduces power). Not changed.

## 6. Pre-human hardening (CM-8R) — 10/10 gates

- **Ghost pilot:** BRP_control held-out TEST = 0.0785 (target 0.10), 118 ghost participants,
  5,964 forecasts, 0 missing events.
- **Monte Carlo:** type-I under the null calibrated (finite-B artifact ruled out).
- **Realtime engine:** offline (no Qwen/LLM/internet), transactional, full trial lifecycle;
  total critical path p95 = 478 ms, cold first trial = 876 ms.
- **Chaos:** 7/7 injected faults handled loudly.
- **Privacy:** 12/12 tests (PII detection/redaction, pseudonymization, encryption at rest,
  no remote telemetry).
- **Clean-room:** bit-identical re-fit (SHA-verified).
- **BRP red team:** 7/9 adversarial cases produce a misleading high BRP; secondary
  diagnostics reveal the modes; BRP stays PRIMARY.

## 7. Discussion

The contribution is the **bridge** from prediction to intervention: (1) a demonstration that
the observational thought stream is not causally identifiable (so a randomized design is
required), (2) a causal method **validated** on an independent public dataset before being
applied to the real question, and (3) a **frozen, pre-human-hardened** confirmatory design.
The human run is blocked only on ethics approval and a pilot. A positive or a null is a
result; the protocol is not to be changed to chase a positive.

## 8. Limitations

- The confirmatory human experiment is **not yet run** (ethics-gated).
- The CM-7 validation is on a clinical iEEG population (no sham; retrieved, not free,
  semantic state).
- N=20 is under-powered for small effects (documented).
- The BRP has known failure modes (magnitude-only change, lexical echo, tiny-basin
  miscalibration, volatility); secondary diagnostics are reported alongside it.
- No free-will claim.

## 9. Conclusion

Prediction is not intervention. We show the observational thought stream is not causally
identifiable, validate a causal-inference method on an independent public dataset, and
freeze a pre-human-hardened randomized confirmatory design. The remaining step — the human
experiment — is blocked only on ethics approval and a pilot.

## References

(To be completed at submission. Cite: ds005494 (Herrema & Kahana); the identifiability
audit; the subject-clustered permutation estimator; the predicted-future-basin estimand.
Internal artifacts cited by SHA in `docs/claims/evidence_matrix.md`.)
