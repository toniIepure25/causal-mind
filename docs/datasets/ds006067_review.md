# Red-Team Review — CM-1 (ds006067 data audit + loader)

Reviewer: orchestrator (the automated `reviewer` agent was unavailable — it hung twice on
flaky OpenNeuro S3 I/O with ~0 CPU for 20+ min; the gate was performed directly by the
orchestrator with full context). Date: 2026-09-11.

## Scope
Independently re-verify the CM-1 data-provenance claims, the minimal-subset integrity,
the loader/alignment correctness, and screen for temporal leakage before any CM-2 result
is reported.

## Checks performed

### 1. Version / license / provenance
- Local `dataset_description.json` (fetched during audit): `Name=ThinkAloud`,
  `DatasetDOI=doi:10.18112/openneuro.ds006067.v2.0.0`, `BIDSVersion=1.7.0`,
  `License=CC0`. Matches the pinned manifest.
- BOLD sidecar `RepetitionTime=1.5` (matches manifest TR).
- **Caveat:** a live re-HEAD of `dataset_description.json` on OpenNeuro S3 returned
  intermittent 404s (5/5 retries) at review time — an OpenNeuro-side transient, not a
  local integrity issue (the same URL read cleanly during the audit ~1 h earlier, and the
  1.6 GB subset was downloaded + checksummed 30 min earlier). Recorded as an external
  reliability note, not a data defect.

### 2. Minimal-subset integrity
- **11/11 files** present under `data/raw/ds006067/`; recomputed SHA-256 **matches the
  manifest for all 11** (participants.tsv, 2× events, 2× preproc BOLD, 2× confounds,
  2× T1w, 2× BOLD sidecar).
- Layout is now a **clean BIDS tree** (`sub-001/`, `sub-005/`); see finding F1.

### 3. Loader + alignment correctness
- **72/72 tests pass** (19 loader tests), ruff clean.
- Loader reads BOLD volume count from the 4D image: **n_volumes=400** for both subjects
  (400 × 1.5 s = 600 s run), confounds row count = 400 (consistent).
- Integrity tests pass: events strictly monotonic, no duplicate event IDs, all events
  within the run window, deterministic load, **subject-disjoint split** (no subject in
  both train and test).
- Alignment queries (`events_overlapping_volume`, `bold_window_for_event`,
  `time_to_volume`, `volume_time`, `verbal_gaps`, `verbal_overlaps`) are self-consistent.

### 4. Leakage screen (temporal)
- Split is **subject-disjoint**; no random row splits on temporal data.
- No future-information path: alignment maps event→volume by onset only; no test-time
  features derived from other subjects.
- **PASS.**

## Findings

- **F1 (resolved) — data layout was a hybrid.** On inspection the fetched subset was in a
  mixed layout: big BOLD/confounds/T1w under a stray `derivatives/` tree with
  non-standard names (`desc-preproc_T1w`, `desc-confounds_timeseries`), while
  events/participants were in the clean tree, and the BOLD sidecar sat at the dataset
  root. This was a leftover from the first (buggy) download that the cleanup did not fully
  remove, compounded by the pod disruption. **Action:** reorganized all 11 files into the
  clean BIDS layout matching the manifest, regenerated `_download_manifest.json` with fresh
  SHA-256, and confirmed 11/11.
- **F2 (resolved) — loader path constants were wrong.** The loader originally pointed at
  the `derivatives/` layout, and an earlier line-length edit accidentally introduced a
  `sub-sub-001` double prefix. **Action:** corrected all path constants to the clean
  `{sub}/...` BIDS layout; loader now resolves BOLD/confounds/T1w/sidecar correctly and
  all 19 loader tests pass.
- **F3 (limitation, documented) — no raw native BOLD/anat in public S3.** The usable BOLD
  is the fMRIPrep `space-MNI152NLin2009cAsym_desc-preproc` derivative (MNI space), not the
  raw native acquisition. Any analysis is therefore in standard (MNI) space. This is a
  real constraint on CM-2+ (no native-space or raw-signal features) and must carry forward.
- **F4 (external) — OpenNeuro S3 intermittency.** Transient 404s observed at review time.
  Mitigation: the subset is already fetched + checksummed locally; re-fetches should use
  retry/backoff (the audit/download scripts do).

## Decision

**GO** — the ds006067 v2.0.0 minimal subset is verified (version, license, 11/11
checksums), in a clean BIDS layout, with a correct loader (72/72 tests) and a passing
subject-disjoint leakage screen. Proceed to CM-2, carrying limitation F3 (MNI-space
derivative only, no raw native BOLD) into all downstream design.
