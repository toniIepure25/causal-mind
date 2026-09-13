# CM-5 Frozen Protocol — NEURAL INCREMENTAL FUTURE INFORMATION

**Status:** FROZEN + SEALED before any decisive neural outcome.
**Anchor:** `23d20f1` (frozen CM-3 provenance).
**Core question:** Does brain activity contain prospective information about
future thought that is not already recoverable from observable thought history?

Decisive contrast: `M4 = behavior + nuisance + neural` vs `M2 = behavior + nuisance`
(IncrementalNeuralGain), NOT `fMRI -> future` alone.

## 1. Split and cohort

- Preserve the CM-2/CM-3 subject-disjoint split (83/18/17, seal `67505261…`) so the
  behavioral baseline is directly comparable.
- **MRI-eligible subset** handled PROSPECTIVELY: eligibility is determined from
  MRI QC/metadata only (no inspection of future-prediction outcomes). Exclusions
  documented, protocol amended, eligible subset resealed + hashed BEFORE decisive
  neural outcomes. No silent dropping of bad-performing subjects.

## 2. Formal prediction time (HRF-safe)

For target thought `T[t+h]` with MRI onset `o_{t+h}` (seconds, from OSF
`start_time`, confirmed in the MRI time base):

- **`prediction_cutoff = o_{t+h} - B`**, with frozen **HRF-safe buffer B = 6 s**
  (~4 TRs at TR=1.5 s).
- Every feature (neural, behavioral, nuisance) must be available at or before
  `prediction_cutoff`. The dataset builder makes it impossible to retrieve the
  target transcript, target annotations, post-cutoff BOLD, future confounds, or
  test-subject-fitted statistics. Unit tests enforce this contract.

Alignment strategies (all sealed; the primary claim must survive the
conservative one):
- **A. Strict pre-target:** BOLD volumes with acquisition time `T < o_{t+h}`.
- **B. HRF-safe buffer (PRIMARY):** BOLD volumes with `T < o_{t+h} - B`.
- **C. Lagged neural history (PRIMARY features):** neural window = BOLD volumes in
  `[o_{t+h} - B - W, o_{t+h} - B]`, frozen **W = 15 s** (10 volumes). All volumes
  are ≥ B s before the target onset.
- **D. Deconvolution / latent estimate:** secondary only, assumptions documented.

Rationale: the BOLD at time T integrates neural activity from before T; a volume
acquired at `T < o_{t+h}` cannot yet reflect the target's own neural activity, and
the 6 s buffer adds a conservative margin for the HRF early rise + onset timing
uncertainty.

## 3. Neural feature ladder (low capacity first)

- **N0 — nuisance-only control (mandatory):** confounds without BOLD. Detects
  whether motion/speech artifacts alone predict the future.
- **N1 — global/network BOLD:** DMN, frontoparietal/control, salience, language
  cortex, medial temporal/hippocampal (where the atlas/resolution permits).
- **N2 — atlas parcellation:** a fixed whole-brain atlas (chosen before outcomes);
  parcel time series; all transforms fitted on TRAIN only.
- **N3 — train-fitted dimensionality reduction:** PCA / regularized latent
  projection, fitted on TRAIN only.
- **N4 — small learned encoder:** only if N1–N3 show genuine signal; small and
  sample-efficient (no giant fMRI transformer).

## 4. Speech / motor confound

Participants are speaking. Quantify the shortcut
`speech -> BOLD/motion -> language -> apparent future prediction`. Controls:
motion regressors, framewise displacement, DVARS, CompCor/confounds, speech
timing/rate, utterance duration, word rate, silence intervals. Compare
`M_confounds` vs `M_behavior` vs `M_behavior + confounds` vs
`M_behavior + confounds + neural`. A neural result is rejected if explained by
speech/motion metadata.

## 5. Frozen model comparisons (per horizon h)

- **M0 — behavioral frozen baseline:** the frozen CM-3 non-neural model (no
  retuning on CM-5 outcomes).
- **M1 — neural only:** brain history -> future (scientific interest, not
  sufficient for PASS).
- **M2 — behavior + nuisance.**
- **M3 — behavior + neural.**
- **M4 — behavior + nuisance + neural (primary conservative model).**
- Decisive contrast: **`M4 - M2`** (IncrementalNeuralGain).

**Mandatory residual test:** `future_hat = behavior_hat + neural_residual_hat`;
equivalently test `brain_t -> e_{t+h}` where `e_{t+h} = true_future -
behavioral_prediction`. If brain predicts the behavioral model's held-out
residuals, neural data contains information absent from observable history.

## 6. Frozen horizons

Primary: **h = 1, 3, 5, 10** (immediate / CM-2 scale / intermediate / CM-3
behavioral lower-bound TPH). Full h=1..10 curve is secondary. **Neural horizon
extension** (does brain extend TPH beyond behavioral?) is tested only after the
predefined comparisons, under a separately sealed protocol.

## 7. Three types of neural value (reported separately)

1. **Incremental accuracy** (does brain improve the prediction score).
2. **Incremental information** (variance/information not in behavioral history).
3. **Individual consistency** (gain across participants, not a few subjects).

## 8. Model family

Ridge / elastic-net / small linear fusion first; PLS/CCA only if justified.
Compact MLP / temporal encoder only if a properly regularized linear model is
clearly beaten. (CM-2/CM-3 showed larger/nonlinear is not automatically better.)

## 9. Negative controls (mandatory)

- **NC1 subject permutation** (behavior paired with wrong subject's neural).
- **NC2 temporal shift** (neural shifted to destroy coupling, preserve
  autocorrelation).
- **NC3 within-subject block permutation.**
- **NC4 nuisance-only** (motion/speech metadata, no BOLD).
- **NC5 neural feature randomization** (destroy spatial structure).
- **NC6 target permutation** (frozen valid procedure).
A real neural gain must collapse under the relevant destructive controls.

## 10. Statistics

Subject-level primary inference: mean IncrementalNeuralGain, 95%
subject-bootstrap CI, per-subject distribution, permutation p, standardized
effect size, proportion of subjects with positive gain. Do not treat 6000
thoughts as 6000 people. Correct if multiple primary horizons/representations are
confirmatory.

## 11. Gates

- **N-GATE 0 ACCESS:** official versioned neural derivatives + provenance.
- **N-GATE 1 ALIGNMENT:** OSF events and BOLD timelines align reproducibly.
- **N-GATE 2 PROSPECTIVE SAFETY:** primary neural features available before the
  target; survive conservative HRF analysis.
- **N-GATE 3 INCREMENTAL VALUE:** M4 significantly beats M2 on frozen
  subject-disjoint test.
- **N-GATE 4 NULL SURVIVAL:** signal collapses under destructive controls.
- **N-GATE 5 CROSS-SUBJECT ROBUSTNESS:** not driven by a few test subjects.
- **N-GATE 6 RED TEAM:** GO.

Decisions: `CM5_PASS_INCREMENTAL_NEURAL_FUTURE_INFO` /
`CM5_PASS_NEURAL_ASSOCIATION_ONLY` / `CM5_NULL_NO_INCREMENTAL_NEURAL_VALUE` /
`CM5_ITERATE` / `CM5_BLOCK`. A clean null is a valid result; gates are not
weakened to force a neural result.

## 12. Claims (only after red-team GO)

- Neural-only association: "Brain activity contains information associated with
  subsequent thought states."
- Fusion beats behavior: "Brain activity contains prospective information about
  future thought not fully recoverable from observable thought history."
- Horizon extension: "Neural state extends the empirically measurable predictive
  horizon beyond behavioral history alone."
- NEVER: thoughts predetermined / brain decides before consciousness /
  determinism proven / free will disproven / causal neural antecedent (those need
  later intervention phases).
