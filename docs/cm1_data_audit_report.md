# CM-1 — DATA AUDIT (ds006067) — Final Report

**DECISION: GO** — proceed to CM-2 (Thought State representation) + non-neural NEXT baselines.

| Field | Value |
|---|---|
| DATASET | OpenNeuro **ds006067** — "ThinkAloud" (continuous spontaneous speech + fMRI) |
| VERSION | **v2.0.0** — `doi:10.18112/openneuro.ds006067.v2.0.0` (pinned, re-verified) |
| LICENSE | **CC0** (public domain) |
| SUBJECTS | **118** total; minimal subset fetched = **2** (sub-001, sub-005) |
| RUNS | 1 session, 1 run/subject, **600 s** each |
| TR | **1.5 s**, **400 volumes** (400 × 1.5 = 600 s) |
| RAW SIZE | Raw native BOLD/anat **NOT in public S3** (HTTP 404) — N/A for public download |
| DERIVATIVES SIZE | **224.75 GB** total (all fMRIPrep derivatives); minimal subset **1.6 GB** |
| TRANSCRIPTS | BIDS `events.tsv`: `onset` / `duration` / `transcript` (spoken sentences) |
| TIMESTAMP GRANULARITY | **Sentence-level** (onset + duration, seconds). **No word-level** timestamps |
| ANNOTATIONS | **None** — no topic labels, no word-level, no sentiment |
| MINIMAL SUBSET | sub-001 + sub-005: preproc BOLD, confounds, T1w, transcripts, BOLD sidecars = **11 files** |
| DOWNLOAD STATUS | **Complete** — 11/11 files, **SHA-256 verified** against manifest |

## Alignment
- Event→volume mapping by onset: `volume = floor(onset / TR)`, 1-indexed.
- Queries implemented: `events_overlapping_volume`, `bold_window_for_event`,
  `time_to_volume`, `volume_time`, `verbal_gaps`, `verbal_overlaps`.
- Note: last thought of sub-001 ends ~610.6 s, ~10 s past the 600 s BOLD end (clipped).

## Integrity tests
**72/72 passing** (19 loader tests), ruff clean. Loader tests cover: monotonic events,
no duplicate IDs, events within run window, deterministic load, BOLD n_volumes=400,
confounds rows=400, alignment-query self-consistency, and **subject-disjoint split**.

## Red-team (leakage) audit
**PASS.** Subject-disjoint split (no subject in both train/test); no random row splits on
temporal data; alignment uses onset only (no cross-subject or future information).
Findings: **F1** hybrid data layout (stray `derivatives/` tree) → reorganized to clean BIDS
layout, 11/11 re-checksummed; **F2** loader path constants wrong (`sub-sub-001` double
prefix) → corrected to `{sub}/...`; both fixed and re-verified.

## Limitations (carry into CM-2+)
1. **MNI-space derivative only** — usable BOLD is fMRIPrep
   `space-MNI152NLin2009cAsym_desc-preproc`; **no raw native BOLD/anat** in public S3.
   No native-space or raw-signal features are available.
2. **Sentence-level transcripts** — no word-level timestamps; alignment granularity is
   bounded by sentence onsets.
3. **2-subject minimal subset** — sufficient for loader/alignment validation, not for
   statistics; full 118-subject fetch (224.75 GB) is a later step.

## Git
- `1c5b3a3` audit · `51f71cc` subset · `d1c8d9b` loader · `b06680d`/`debd860` loader path fix
- `3892299` red-team review (GO)
- All CM-1 tasks in `done/`: AUDIT, SUBSET, LOADER, REVIEW.
