# ds006067 — Authoritative Data Audit (CM-1)

Dataset: **ThinkAloud** (OpenNeuro `ds006067`)
Audited: 2026-09-11 · Auditor: data agent (research) + orchestrator (verification)
Method: OpenNeuro public S3 bucket `openneuro.org`, prefix `ds006067/`
(50,227-entry paginated file listing + small metadata files only; **no bulk NIfTI downloaded**).
Reproducible via `data/scripts/audit_ds006067.py`.

> **Network note (verified 2026-09-11):** `api.openneuro.org` returns NXDOMAIN and
> `openneuro.org/crn/...` REST paths 404 from the pod. The authoritative, reachable
> file-level source is the public S3 bucket **`openneuro.org`** (NOT `openneuro`),
> discovered from `openneuro.org/crn/config.js` → `AWS_S3_PUBLIC_BUCKET`. All facts
> below were read from that bucket.

## Verified facts (each with source)

| Fact | Value | Source |
| --- | --- | --- |
| Dataset ID | `ds006067` | S3 prefix |
| Pinned version / DOI | **v2.0.0** — `doi:10.18112/openneuro.ds006067.v2.0.0` | `dataset_description.json` → `DatasetDOI` |
| Name | ThinkAloud | `dataset_description.json` → `Name` |
| License | **CC0** (public domain) | `dataset_description.json` → `License` |
| BIDS version | 1.7.0 | `dataset_description.json` → `BIDSVersion` |
| Task | `thinkaloud` — "Subjects say out loud their stream of thoughts for 10 minutes" | `task-thinkaloud_bold.json` → `TaskDescription` |
| Authors | Hongmi Lee, Xian Li, Savannah Born, Christopher Honey, Janice Chen | `dataset_description.json` |
| Primary citation | Su, Li, Born, Honey, Chen, Lee, 2025. *Neural dynamics of spontaneous memory recall and future thinking in the continuous flow of thoughts.* Nat Commun 16, 6433. doi:10.1038/s41467-025-61807-w | `dataset_description.json` → `HowToAcknowledge` |
| **Subjects** | **118** | S3 `sub-*/` dirs = 118; matches `participants.tsv` rows (118) |
| Sessions | 1 (single session per subject) | BIDS layout (no `ses-*` dirs) |
| Runs | 1 run/subject (`task-thinkaloud`) | one `events.tsv` + one preproc BOLD per subject |
| **TR** | **1.5 s** | `task-thinkaloud_bold.json` → `RepetitionTime`; confirmed by confounds (400 rows) |
| Volumes / run | **400** (400 × 1.5 s = **600 s** ≈ 10 min) | `desc-confounds_timeseries.tsv` data-row count |
| Scanner / site | Philips, Kennedy Krieger Institute | `task-thinkaloud_bold.json` |
| Acquisition | multiband accel 4, flip 52°, slice thickness 2 mm, PE `j-`, EPI field maps (`dir-AP_epi.json`, `dir-PA_epi.json`) | `task-thinkaloud_bold.json`, root epi sidecars |
| Demographics | `participants.tsv`: `participant_id, age, sex` (age 18–39, M/F) | `participants.tsv` |

## Transcripts & annotations

- **Transcript file:** `sub-XXX/func/sub-XXX_task-thinkaloud_events.tsv` (BIDS events), one per subject (118 files).
- **Columns (3):** `onset` (s), `duration` (s), `transcript` (free text).
  - `onset`/`duration` in **seconds** from scan start; `transcript` = the spoken sentence/thought.
  - sub-001: **65** thought rows; first onset 9.59 s; last row ends 597.14 + 13.47 = **610.61 s**.
- **Granularity:** **sentence/thought-level only.** Each row = one thought (one utterance segment).
  - **No word-level timestamps.**
  - **No explicit "thought boundary" flag** — the sentence segmentation IS the boundary.
  - **No category / topic / psychological label columns** — `transcript` is raw text only.
  - Any semantic/topic encoding must be computed downstream (e.g., via an LLM), not read from the dataset.
- **Gaps/overlaps:** thoughts are near-continuous but have silent gaps between rows (e.g. row 1 ends 22.68 s, row 2 onset 22.7 s). Loader must treat inter-row time as silent.

## Raw vs derivatives (CRITICAL provenance finding)

- **Raw native-space BOLD and raw anatomical NIfTI are NOT present in the public S3 prefix.**
  - `ds006067/sub-001/func/` contains **only** `sub-001_task-thinkaloud_events.tsv`.
  - `ds006067/sub-001/anat/` is **empty**.
  - `HEAD ds006067/sub-001/func/sub-001_task-thinkaloud_bold.nii.gz` → **HTTP 404**.
  - No versioned prefix (`ds006067/ds006067_v2.0.0/`, `ds006067/raw/`) exists.
  - The raw `task-thinkaloud_bold.json` sidecar exists (so the raw run is *described*) but the raw NIfTI is not publicly served here.
- **All 2,593 NIfTI files are under `derivatives/`** (fMRIPrep + FreeSurfer), 224.75 GB total.
  - Usable BOLD for modeling = fMRIPrep **`space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz`** (MNI152NLin2009cAsym, 1.5 s, 400 vols), ~771–791 MB/subject.
  - Also present: `..._smooth4mm_denoise_bold`, `desc-confounds_timeseries.tsv`, coreg/hmc boldref, image transforms, fsaverage6 surface `.func.gii`, FreeSurfer probseg (GM/WM/CSF), `dseg`, `desc-preproc_T1w`, brain masks, and `derivatives/sourcedata/` (FreeSurfer, 35.26 GB / 40,187 files).

## Footprint

| Component | Files | Size |
| --- | --- | --- |
| Raw metadata + transcripts (S3) | 129 | ~1 MB |
| Derivatives (fMRIPrep + FreeSurfer) | 50,098 | **224.75 GB** |
| **Total public S3** | 50,227 | **224.75 GB** |

## Minimal useful subset (for CM-1 validation)

Two subjects (sub-001, sub-005) end-to-end, **≈ 1.6 GB**:

| File (per subject) | Size |
| --- | --- |
| `sub-XXX/func/sub-XXX_task-thinkaloud_events.tsv` (transcript) | ~7 KB |
| `derivatives/sub-XXX/func/..._space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz` | ~771–791 MB |
| `derivatives/sub-XXX/func/..._desc-confounds_timeseries.tsv` | ~2 MB |
| `derivatives/sub-XXX/anat/sub-XXX_desc-preproc_T1w.nii.gz` | ~16–17 MB |

Plus global: `participants.tsv`, `dataset_description.json`, `task-thinkaloud_bold.json` (< 3 KB).

## Alignment model (time zero, units, clock)

- **Time zero:** `events.tsv` `onset = 0` ↔ BOLD **volume 1** (t = 0). Same clock, both in seconds.
- **Volume k** spans `[ (k-1)·TR , k·TR )` = `[ (k-1)·1.5 , k·1.5 )` seconds.
- **Thought i** spans `[ onset_i , onset_i + duration_i )`.
- **Overlap query:** thought i overlaps volume k iff the two half-open intervals intersect.
- **HRF:** NOT applied by the loader. The BOLD is the measured signal; any HRF deconvolution/convolution for prospective prediction is a *modeling* choice to be made explicitly in CM-2/CM-3, never silently in the loader.
- **Boundary caveat:** the last thought of sub-001 ends at ~610.6 s, **~10 s past** the 600 s BOLD end. Thoughts whose onset+duration exceeds 600 s have no (or partial) BOLD coverage and must be clipped/flagged by the loader.

## Does the dataset support NEXT-THOUGHT prospective evaluation?

**Yes, with caveats.**
- Thoughts are temporally ordered with clean `onset`/`duration`; thought N+1 strictly follows thought N → a well-defined prospective target.
- BOLD (1.5 s, 400 vols) is temporally aligned to the same clock → can condition a predictor on the BOLD window preceding a thought onset.
- **Caveats:** (1) sentence-level timestamps only (no word-level); (2) no built-in topic/semantic labels — "next thought" is free text, so a semantic encoder (e.g. LLM embedding) is required to make prediction meaningful; (3) usable BOLD is MNI-space fMRIPrep preprocessed (raw native not public); (4) final ~10 s of thoughts may exceed BOLD coverage.

## Unverified / open items

- Exact reason raw native BOLD is absent from public S3 (may be datalad/annex-gated or withheld); **does not block CM-1** because the fMRIPrep preproc BOLD is public and sufficient.
- Whether all 118 subjects have identical 400-volume BOLD and uniform events.tsv schema (loader integrity tests will check the fetched subset; a full-cohort check is a CM-2 task).
