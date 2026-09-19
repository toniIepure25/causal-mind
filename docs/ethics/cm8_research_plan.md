# CM-8 Research Plan / Final Protocol (v1.0 — FROZEN)

- **Version:** 1.0 (frozen for ethics submission). Do not modify without an explicit,
  logged amendment.
- **Study title:** *Causal Redirection of a Predicted Semantic Thought Trajectory: a
  randomized within-subject experiment (Pre-Oracle / "Break the Chain").*
- **Type:** behavioral, within-subject, randomized, single-site (University of Vienna).
- **Status:** data-independent; NO human data collected. Gated on ethics approval.

## 1. Scientific rationale

CM-2/3 established that cognitive history predicts future thought semantics
(`history -> future`). CM-6 showed observational structure cannot establish causality. CM-7
validated the causal-intervention machinery on a public randomized dataset (null effect).
CM-8 is the first own experiment, engineered to test whether a deliberate or
externally-induced intervention **causally redirects a predicted semantic trajectory**. This
is PRE-ORACLE: the participant is NOT shown the model's exact next-thought prediction.

## 2. Hypotheses

- **H1 (endogenous):** a deliberate "move your thinking away" instruction increases the
  probability that the subsequent trajectory leaves the predicted semantic basin, vs
  CONTROL/SHAM.
- **H2 (exogenous):** an external semantic cue increases that probability, vs CONTROL/SHAM.
- **H3 (sham no-op):** SHAM ≈ CONTROL (the sham does not itself shift the trajectory).
- **H4 (persistence):** any redirection persists beyond the immediate one-step and is not
  explained by cue repetition.

## 3. Conditions (four, distinct)

- **CONTROL:** "Keep thinking naturally. There is nothing special about this moment."
  (neutral, matched length; no redirection content.)
- **SHAM:** a matched-length, matched-attention neutral prompt ("continue as you were")
  with identical UI/timing/cue frame, but **no** redirection content. Tests demand/attention
  /interruption only.
- **GENERAL REDIRECT:** "Now deliberately move your thinking away from what you have been
  thinking about. Do not repeat those ideas — let your mind go somewhere else." (no target.)
- **SPECIFIC CUE:** a single externally supplied semantic cue (a word/phrase from a
  predefined alternative basin) intended to steer the trajectory toward that basin.

Reference arm: pooled CONTROL/SHAM (primary); SHAM-alone (pre-specified sensitivity). H3
(SHAM vs CONTROL) pre-specified with a fallback: if H3 is significant, SHAM-alone is the
primary reference.

## 4. Trial timeline

1. Baseline thinking window (free verbalization/typing, ~fixed duration or N thoughts).
2. Online state estimation (frozen MiniLM embeddings of the recent thought window).
3. Future forecast (frozen predictor → predicted future at horizon `h*`; predicted-future
   basin, radius `r_α` pre-calibrated).
4. Randomization (assign the condition from the frozen per-subject manifest).
5. Intervention (present the condition's instruction/cue).
6. Post-intervention thinking window (capture the subsequent thought sequence).
7. Outcome extraction (BRP at `h*`, divergence, latency, persistence, return, decay).
8. Optional self-report (effort / intentionality / perceived success; kept separate).

## 5. Randomization

- Unit: the trial. Within-subject; each subject experiences all four conditions.
- Counterbalanced randomized sequence; each condition an equal number of times; no more
  than 2 consecutive trials of the same condition.
- Seed + full per-subject condition manifest frozen and stored in
  `data/manifests/cm8_randomization_manifest.json`.

## 6. Participants and trials

- **N = 20 completed subjects** (recruit 25 at 20% attrition), **24 trials/subject**
  (from the simulation-based power analysis: ~80% power for a BRP difference ≈ 0.11 at
  α=0.05, ICC≈0.2).
- **Inclusion:** healthy adults, age 18–35, native/fluent [language], normal or
  corrected-to-normal vision, right-handed (to be finalized).
- **Exclusion:** current neurological/psychiatric condition affecting thought or speech,
  inability to complete the task, (to be finalized with the supervisor).

## 7. Primary endpoint

- **BRP** at the frozen horizon `h*` (target `h* = 2` thought events, finalized at the
  preregistration seal): P(observed future leaves the predicted-future basin | intervention).
- **Primary ATEs:** `ATE_GENERAL` and `ATE_CUE` (BRP difference vs pooled CONTROL/SHAM),
  estimated separately; subject-clustered permutation test, **two-sided α = 0.05**,
  B = 10,000. BH-FDR q = 0.05 over the primary family {ATE_GENERAL, ATE_CUE}.

## 8. Secondary endpoints (predefined, EXPLORATORY)

Divergence, redirection latency, persistence horizon, return probability, effect decay
(per-horizon); SHAM vs CONTROL (H3); endogenous-vs-exogenous comparison (only if both H1
and H2 significant); subjective effort / success awareness. These are hypothesis-generating
and CANNOT rescue a null primary or select a significant horizon after the fact.

## 9. Semantic basin definition

Predicted-future basin = ball around the frozen predictor's forecast at `h*`, radius
`r_α` = the held-out (1 − 0.10) quantile of the predictor's error norm (calibrated on
no-intervention data from the SAME capture modality). `leave = 1{ ‖observed − forecast‖ >
r_α }`. One basin metric frozen at the preregistration seal. (See
`docs/cm8_basins_brp.md`, `src/causal_mind/causal/predicted_basin.py`.)

## 10. Prediction model freeze

The forecasting model (a CM-3-style model fit on historical/pilot data) is FROZEN before
the confirmatory experiment; NOT retrained on confirmatory outcomes. Adaptive/personalized
predictors are a later secondary study only.

## 11. Stopping rules

- **Safety/ethics stop:** any adverse event, participant distress, or ethics concern →
  immediate pause; resume only with supervisor + ethics sign-off.
- **Data-quality stop:** if the pilot shows the capture modality cannot reliably segment
  thoughts or the predictor latency exceeds the inter-thought gap, the protocol is revised
  (amendment) before the confirmatory run.
- **No futility stop** on the primary (a null is a valid result); the trial count is fixed
  a priori.

## 12. Handling of failed / incomplete trials

- A trial is excluded only for a pre-specified technical failure (capture dropout, a window
  with < N_min valid embeddings), defined before any outcome is seen.
- No outcome-based exclusion. Intent-to-treat: all randomized trials analyzed, condition
  as-assigned.
- A subject is retained if ≥ 16 of 24 trials are valid (threshold frozen before outcomes).

## 13. Participant withdrawal

- Voluntary; may stop at any time without consequence or penalty.
- Data collected before withdrawal are retained (analyzed) unless the participant requests
  deletion within the withdrawal window (see the data management plan for the limits).

## 14. Compensation (assumption — HUMAN INPUT REQUIRED for final amount)

- Assumed: a modest fixed compensation per completed session (typical for behavioral
  studies), paid only for completed sessions. **Exact amount and payment method: HUMAN INPUT
  REQUIRED** (supervisor/institutional policy).

## 15. Expected duration

- Assumed: ~45–60 minutes per session (24 trials + breaks + setup/debrief). **To be
  confirmed in the pilot.**

## 16. Debrief procedure

Full explanation of the study's purpose, the four conditions (including the sham), the
randomization, and the (non-)results. Opportunity to ask questions and to request
raw-text destruction. (See `docs/ethics/cm8_debrief.md`.)

## 17. Capture modality

Pilot decision (CM-8P): continuous think-aloud vs typed stream vs intermittent probes,
chosen on temporal resolution, semantic richness, fatigue, and reactivity. The primary
modality is frozen after the pilot (not assumed).

## 18. Claim boundary

Even on a PASS: do NOT claim "free will exists." The justified ceiling: *deliberate
cognitive-control instructions (or an external semantic cue) causally alter the
distribution of subsequent thought trajectories under the tested conditions.* The
endogenous-vs-exogenous contrast is confounded (disclosed) and is secondary/exploratory.
