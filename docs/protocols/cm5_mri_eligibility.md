# CM-5 MRI Eligibility Protocol

**Status:** FROZEN + HASH-SEALED before any decisive neural outcome.
**Amends:** `docs/protocol/cm5_frozen_protocol.md` §1 (MRI-eligible subset),
prospectively, BEFORE any neural prediction outcome is inspected.
**Amendment ID:** CM5-ELIG-1 (includes steady-state target refinement AM-1).

## 0. Scope and integrity attestation

- Eligibility is determined from **outcome-independent** information only:
  OpenNeuro snapshot 2.0.0 metadata (git mirror clone, annex keys/sizes),
  fMRIPrep confounds TSVs (motion/volume QC), and the frozen behavioral
  representation (ThoughtStateV1). **No neural prediction outcome** (no
  M0-M4 score, no IncrementalNeuralGain, no per-subject neural metric) is
  used anywhere in this protocol.
- The N=2 real-data smoke (sub-001/sub-005, M2=0.8847, M4=0.8482,
  gain=-0.0365) is an **L0 pipeline-validation artifact**. It computed a
  neural number on 2 subjects; it is attested here as EXCLUDED from all
  eligibility, model-selection, and threshold decisions. The "no outcome
  inspected" scope is: **no decisive (cohort-level, subject-disjoint)
  outcome has been inspected**; the criteria below derive only from
  metadata + confounds + behavioral timing.
- After sealing, cohort membership may NOT change because of model
  outcomes. Post-acquisition gates (§6) may only REMOVE subjects on
  pre-registered data-quality grounds, documented in a sealed amendment
  before any decisive analysis.

## 1. Data availability (A)

A subject is eligible only if ALL of the following hold:

- **A1** MNI preprocessed BOLD
  (`{sub}_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz`)
  exists in snapshot 2.0.0 AND is retrievable via the official OpenNeuro
  authenticated path with the **URL-path identity guard** active: the
  resolved S3 URL path must equal the requested dataset path, and the
  resolved object size must equal the annex-key size. Mismatch => refuse.
- **A2** Brain mask
  (`..._space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz`) exists.
- **A3** Confounds TSV (`..._desc-confounds_timeseries.tsv`) exists and is
  retrievable with the same guard.
- **A4** BOLD JSON + confounds JSON metadata exist (in-git).
- **A5** OSF thought stream present: ThoughtStateV1 file with valid,
  strictly-monotonic `start_time` (verified in CM-1/CM-2 integrity checks).
- **A6** Raw MRI `events.tsv` present (MRI time base, CM-5A access audit).

Smooth4mm derivatives are NOT required (per mission; N1-N3 use the
unsmoothed MNI BOLD).

**Guard-fire log (sub-002, re-tested live 2026-09-14 after API restoration):**
the OpenNeuro API resolves ALL of sub-002's annexed derivative files (BOLD,
confounds TSV, masks) to pointer objects (`/crn/datasets/ds006067/objects/<id>`
with `?filename=...`, sizes 102-107 bytes) instead of content. Re-tested
twice (confounds retry + BOLD URL inspection); the anomaly is consistent,
not transient. The identity guard refused both. sub-002 is therefore
EXCLUDED on data availability (A1/A3). This is a provider-side storage
anomaly (same class as the regression-guarded `bold.json` case), not a
discretionary call. Awareness note (documented per red-team): removing a
TRAIN subject can in principle weaken M0/M2 and inflate M4-M2; under
subject-level inference the effect of 1/83 subjects is negligible, and the
exclusion is mechanical (guard-fire), not selective.

## 2. File validity (B)

- **B1** Confounds row count == 400 volumes (TR=1.5 s, 600 s scan).
- **B2** No missing or non-finite values in the core confound regressors
  (`framewise_displacement`, `dvars`, `std_dvars`, `global_signal`, `csf`,
  `white_matter`, `tcompcor`, `rmsd`) after the first 10 non-steady-state
  volumes (fMRIPrep writes `n/a` for FD/DVARS on volume 1 by design).
- **B3** (post-acquisition, §6) NIfTI readable, expected MNI space
  (`space-MNI152NLin2009cAsym`), TR=1.5 s, 400 volumes, finite data, valid
  affine, valid mask (all-mask values in {0,1}, non-empty).

## 3. Temporal compatibility (C) — includes amendment AM-1

**AM-1 (steady-state refinement, MORE conservative than the frozen protocol):**
the frozen protocol defines the neural window as
`[o - B - W, o - B]` with B=6 s, W=15 s, so targets with onset >= 21 s are
HRF-safe. However, for targets with onset in [21 s, 36 s) the neural window
overlaps the first 15 s of the scan (10 non-steady-state volumes at
TR=1.5 s), where BOLD is unreliable. AM-1 therefore requires, for the
PRIMARY analysis, that the entire neural window lie in steady-state BOLD:

    onset >= N_NONSTEADY*TR + B + W = 10*1.5 + 6 + 15 = 36 s

This tightens (never loosens) the frozen HRF-safety contract.

- **C1** >= **20** steady-state HRF-safe target events, where a target event
  e satisfies `start_time(e) >= 36 s` and
  `start_time(e) + duration(e) <= 600 s`.
  Rationale: the inference unit is the subject (one gain estimate each); the
  floor sets per-subject precision (SE ~ 1/sqrt(20)). Distribution of
  steady-state target counts (n=118): min=15, p10=27, median=48, max=113.
  The floor excludes only subjects at the extreme low tail.

## 4. Imaging / motion QC (D)

Subject-level exclusion if ANY of:

- **D1** mean framewise displacement > **1.0 mm** (first 10 volumes
  excluded from stats, fMRIPrep non-steady-state convention).
- **D2** > **50%** of volumes with FD > 1.0 mm.
- **D3** > **25%** of volumes with FD > 2.0 mm.

**Threshold justification (pre-declared, outcome-independent):**
- The standard strict screen (Power et al. 2018: mean FD > 0.3 mm OR >10%
  of volumes FD > 0.5 mm; Satterthwaite et al. 2013) is documented here as
  **infeasible for this speaking task**: applied to this cohort it would
  exclude **83/117 (70.9%)** of subjects (83 by mean FD > 0.3 alone).
  Participants speak during the scan; median mean FD is 0.397 mm, above any
  resting-state screen.
- The adopted bar (D1-D3) is a severe-motion / data-integrity screen: it
  sits far in the tail (cohort mean-FD p75 = 0.530, max = 1.207) and is
  **robust to the exact value** — any threshold in [0.9, 1.207) excludes the
  same single subject (sub-089), so it cannot have been tuned to outcomes.
- Moderate motion is NOT excluded: it is handled by nuisance regressors in
  M2/M4 (see §8) and tested by the NC4 nuisance-only control. Pre-registerd
  sensitivity analyses S1/S2 (§9) verify the primary contrast is
  threshold-robust.
- Circular-selection concern (select on motion, then regress motion):
  neutral — motion enters BOTH M2 and M4, so it cancels in the decisive
  M4-M2 contrast; selection is subject-level and outcome-independent.

## 5. Behavioral compatibility (E)

- **E1** Transcript present; timestamps strictly monotonic and within the
  600 s scan; ThoughtStateV1 constructs without integrity failure
  (CM-1/CM-2 checks, all 118 subjects passed).

## 6. Post-acquisition gates (F) — pre-registered, applied after BOLD
download and BEFORE feature extraction / any decisive analysis

- **F1** NIfTI validation per B3 (readable, MNI space, TR, 400 volumes,
  finite, valid affine/mask).
- **F2** tSNR gate: tSNR = mean over brain-mask voxels of (volume-mean /
  volume-std) across steady-state volumes. Exclude a subject if
  tSNR < **2.0** OR tSNR is below the **5th percentile** of the acquired
  cohort's tSNR distribution. (Protects against low-SNR subjects whose
  per-subject gain estimate would be unreliable and inflate group variance.)
- Any F-gate exclusion is recorded in a **sealed amendment**
  (`reports/cm5_cohort_amendment_*.json`, hashed) BEFORE feature extraction
  or decisive analysis. F-gates cannot add subjects.

## 7. Split projection (no fresh random split)

The frozen CM-2/CM-3 split (seal `67505261...`, 83/18/17) is PROJECTED onto
the eligible set:

    train_CM5 = eligible ∩ train_CM3
    val_CM5   = eligible ∩ val_CM3
    test_CM5  = eligible ∩ test_CM3

A new split is permitted ONLY if a projected part becomes scientifically
unusable (< 5 subjects), which would require a pre-outcome protocol
amendment. (Not triggered: projected sizes are 79/18/16.)

## 8. Frozen nuisance set for M2/M4 (specification for the decisive run)

M2 and M4 nuisance regressors (per frozen protocol §4), per prediction row
(window-aligned):

- fMRIPrep confounds (window means): `framewise_displacement`, `dvars`,
  `std_dvars`, `rmsd`, `global_signal`, `csf`, `white_matter`,
  `t_comp_cor_00..09` (10), `c_comp_cor_00..` (all available).
- Speech/motor (derived from raw `events.tsv`, window-aligned): utterance
  duration, word rate, silence interval, speech onset lag.
- NC4 (nuisance-only control) uses the SAME nuisance set without BOLD.

## 9. Pre-registered sensitivity analyses (secondary, NOT primary)

- **S1 (strict motion screen):** re-run M4-M2 after additionally excluding
  subjects with mean FD > 0.3 mm OR >10% of volumes FD > 0.5 mm.
- **S2 (top-decile motion):** re-run M4-M2 after additionally excluding the
  top decile of mean FD.
- **S3 (per-horizon counts):** report valid-instance counts per horizon
  (h=1,3,5,10) per subject; confirm no horizon is driven by a handful of
  instances.
If the primary gain survives S1/S2, the "motion handled by nuisance + NC4"
claim is tested rather than assumed; if it collapses, that is reported as
the result.

## 10. Exclusion ledger (all 118 subjects)

| subject | split | criterion | metric value |
|---|---|---|---|
| sub-002 | train | A1/A3 (guard-fire) | API resolves BOLD+confounds to pointer objects (107/102 B); re-tested live, consistent |
| sub-067 | train | C1 | 19 steady-state targets (< 20) |
| sub-087 | test | C1 | 19 steady-state targets (< 20) |
| sub-110 | train | C1 | 15 steady-state targets (< 20) |
| sub-089 | train | D1 | mean FD 1.207 mm (> 1.0); 37.2% vol FD>1.0; 11.8% vol FD>2.0 |

All other 113 subjects pass A-E. Projected split: **train 79, val 18,
test 16** (113 total).

## 11. Machine-readable config + seal

- Config: `configs/cm5_eligibility.json` (thresholds, constants, file list,
  OR-structure).
- Seal: `reports/cm5_cohort_seal.json` — includes included/excluded
  subjects with reasons, split membership, target counts, frozen QC
  thresholds, horizons, B=6 s, W=15 s, models/contrast, protocol + config
  SHA256 hashes, and the QC distribution snapshot.
- After sealing, cohort membership may not change because of model
  outcomes (only §6 F-gates, via sealed amendment).
