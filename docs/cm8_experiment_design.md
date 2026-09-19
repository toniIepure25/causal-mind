# CM-8A — Experimental Design: Causal Redirection of a Predicted Semantic Trajectory

- **Status:** DRAFT for red-team. Data-independent (no human data).
- **Companions:** `docs/cm8_dag.md`, `docs/cm8_basins_brp.md`,
  `docs/research/cm8_literature_audit.md`.
- **Primary outcome:** BRP (see `docs/cm8_basins_brp.md`). **Primary horizon `h*`** frozen
  at the preregistration (target `h* = 2` thought events, pending pilot).

## 1. The four conditions (must remain distinct)

| condition | instruction / stimulus | mechanism tested |
| --- | --- | --- |
| **CONTROL** | "Keep thinking naturally. There is nothing special about this moment." (neutral, matched length) | natural trajectory |
| **SHAM** | A matched-length, matched-attention prompt that says **nothing** about changing semantic direction (e.g., a neutral "continue as you were" prompt with an identical UI/timing/cue frame, but no redirection content) | demand / attention / interruption only |
| **GENERAL REDIRECT** | "Now deliberately move your thinking away from what you have been thinking about. Do not repeat those ideas — let your mind go somewhere else." (no specific target) | **endogenous** voluntary redirection |
| **SPECIFIC CUE** | A single externally supplied semantic cue (a word/phrase from a predefined alternative basin) intended to steer the trajectory toward that basin | **exogenous** causal redirection |

- CONTROL and SHAM are the **reference arms**. The **primary** reference is the pooled
  `CONTROL/SHAM` (per the design spec). Because GENERAL/CUE differ from SHAM only in the
  redirection content, **SHAM alone** is a pre-specified sensitivity reference that
  isolates the active ingredient from the mere prompt/interruption. `SHAM vs CONTROL` is
  pre-specified (H3) to confirm the sham is a true no-op; **if H3 is significant (the
  prompt/interruption itself shifts the trajectory), the SHAM-alone reference becomes the
  primary** (pre-specified fallback).
- GENERAL REDIRECT and SPECIFIC CUE are the **intervention arms**, estimated **separately**
  (never pooled) so the endogenous vs exogenous comparison is clean.

## 2. Sham specification (critical)

The sham must match the active conditions on **instruction exposure, attention,
interruption, expectancy, and experimenter demand**, while omitting the redirection
content. Concretely:
- Same presentation timing, duration, and UI frame as the active cues.
- A neutral prompt of matched word count/complexity.
- No mention of "change direction," "move away," or any semantic target.
- **Red-team must approve the sham** as a true no-op (G7). If the sham itself shifts the
  trajectory (SHAM ≠ CONTROL), the design must be revised before the pilot.

## 3. Randomization

- **Unit:** the trial (each trial = one baseline window + one intervention + one post-window).
- **Scheme:** within-subject, each subject experiences all four conditions across trials.
  Condition order is a **counterbalanced** randomized sequence (each condition appears an
  equal number of times; no more than 2 consecutive trials of the same condition).
- **Seed + manifest:** the randomization seed and the full per-subject condition manifest
  are frozen and stored in `data/manifests/cm8_randomization_manifest.json` (G3).
- **Inference:** subject-clustered permutation test (permute condition labels within
  subjects), as validated in `data/scripts/cm8_synthetic.py` (G2).

## 4. Trial timeline

1. **Baseline thinking window** — participant freely verbalizes/types thoughts (~fixed
   duration or N thoughts).
2. **Online state estimation** — build the current ThoughtState (frozen MiniLM embeddings
   of the recent thought window).
3. **Future forecast** — the **frozen** CM-3-style predictor forecasts the near-future
   semantic state(s) at horizon `h*` (and the predicted-future basin, `r_α` pre-calibrated).
4. **Randomization** — assign the condition for this trial (from the frozen manifest).
5. **Intervention** — present the condition's instruction/cue.
6. **Post-intervention thinking window** — participant continues; capture the subsequent
   thought sequence.
7. **Outcome extraction** — measure the trajectory from the subsequent thought events:
   BRP at `h*`, divergence, latency, persistence, return probability, effect decay.
8. **Optional self-report** — effort / intentionality / perceived success (kept separate
   from the objective outcomes).

Repeat for `trials_per_subject` trials (target 24, per the power analysis).

## 5. Capture modality (pilot decision)

Do NOT blindly reuse ds006067. The pilot (CM-8P) explicitly compares:
- **continuous think-aloud** (highest temporal resolution; verbalization reactivity),
- **typed stream** (lower reactivity for some content; pace change),
- **intermittent probes** (lowest reactivity; coarse temporal precision).

The pilot measures temporal resolution, semantic richness (embedding coverage), fatigue,
and **reactivity** (does reporting itself change the trajectory?). The **primary modality
is frozen after the pilot** (G1/G5), not assumed.

## 6. Predictor freeze (G8)

The forecasting model used to define the predicted basin is **frozen before the
confirmatory experiment** (a CM-3-style model fit on historical/pilot data). It is NOT
retrained on confirmatory outcomes. Adaptive/personalized predictors are a later
secondary study only.

## 7. Endogenous vs exogenous (do not conflate)

- `ATE_GENERAL = E[BRP | do(GENERAL REDIRECT)] − E[BRP | do(CONTROL/SHAM)]` (endogenous).
- `ATE_CUE = E[BRP | do(SPECIFIC CUE)] − E[BRP | do(CONTROL/SHAM)]` (exogenous).
- If **both** work → compare endogenous vs exogenous (the agency question).
- If **only SPECIFIC CUE** works → externally-induced causal control, but not yet voluntary
  self-redirection.
- If **GENERAL REDIRECT works beyond SHAM** → much closer to the agency question.

**Red-team disclosure (independent pass):** the endogenous-vs-exogenous contrast is
**confounded**, not a clean agency test — it conflates (a) voluntary vs external, (b) no
target vs specific target, and (c) a verbal instruction vs a semantic cue. In addition, the
CUE arm's BRP lift is **confounded with semantic priming**: a novel cue word can shift the
trajectory as a mere semantic input, independent of any "redirection." Therefore the
endogenous-vs-exogenous comparison is **secondary/exploratory** and must NOT be read as a
clean "voluntary vs external" or "free-will" result. The primary claims are H1 (GENERAL
works vs reference) and H2 (CUE works vs reference), each a clean single-arm causal
estimand; the agency interpretation requires a future design that separates target-specificity
and cue modality from the endogenous/exogenous factor.

## 8. Trivial-success guard (SPECIFIC CUE)

Frozen (see `docs/cm8_basins_brp.md` §6): primary `h* ≥ 2`; cue-echo exclusion (verbatim /
near-verbatim cue repetitions removed from persistence); beyond-cue movement required;
cue-repetition baseline from the neutral-cue data.

## 9. Sample size (from CM-8E)

Target **N = 20 completed subjects** (recruit 25 at 20% attrition), **24 trials/subject**,
giving ~80% power for a minimally-interesting BRP difference of ~0.11 (BRP 0.10 → ~0.21)
at α=0.05, ICC≈0.2. Larger effects (Δ~0.20) are detectable at N≈10. The minimally-
interesting effect is justified a priori (a clear, reliable shift in the probability of
leaving the predicted basin), NOT reverse-engineered from a pilot.

**Red-team notes (addressed):**
- **Fatigue / learning / strategy adaptation** over 24 repeated trials is a real risk.
  Mitigations: counterbalanced order, no >2 consecutive same-condition trials, short breaks
  between blocks, and the pilot (CM-8P) explicitly measures fatigue and trial-count
  stability; if fatigue dominates, the trial count is reduced (re-powered) BEFORE the
  confirmatory run. The within-subject ICC in the power analysis partly absorbs this.
- **Calibration-set modality:** the held-out set used to calibrate `r_α` must come from the
  SAME capture modality as the experiment (the error distribution is modality-dependent).
  This is a pilot dependency (G1).
- **ICC assumption:** ICC≈0.2 is a planning estimate; the pilot estimates the actual ICC and
  the power is re-checked before the confirmatory run.
