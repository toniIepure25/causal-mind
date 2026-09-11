# ds006067 — Temporal Alignment Convention (CM-1)

Loader: `src/causal_mind/data/ds006067.py` · Tests: `tests/test_ds006067_loader.py`

## Clocks and time zero

- **One shared clock, in seconds.** `events.tsv` `onset`/`duration` and the BOLD
  volume grid use the same time origin.
- **Time zero:** `onset = 0` ↔ **BOLD volume 1** (t = 0). Verified: first thought of
  sub-001 starts at 9.59 s; the run is 400 volumes × 1.5 s = 600 s.
- **Volume grid:** volume `k` (1-indexed) spans the half-open window
  `[(k-1)·TR, k·TR)` = `[(k-1)·1.5, k·1.5)` seconds. Volume 400 spans `[598.5, 600)`.
- **Thought interval:** thought `i` spans `[onset_i, onset_i + duration_i)`.

## Queries the loader answers

| Question | API |
| --- | --- |
| What thought event(s) overlap a given BOLD volume `k`? | `run.events_overlapping_volume(k)` |
| What BOLD window corresponds to a thought? | `run.bold_window_for_event(e) -> (first_vol, last_vol)` |
| Which volume contains time `t`? | `run.time_to_volume(t)` |
| Onset time of volume `k`? | `run.volume_time(k)` |
| Are there gaps/overlaps in the verbal report? | `run.verbal_gaps()`, `run.verbal_overlaps()` |

## HRF handling

**The loader applies NO HRF convolution or deconvolution.** The BOLD is the measured
signal at 1.5 s resolution. Any HRF modeling for prospective (NEXT-THOUGHT) prediction
is an **explicit CM-2/CM-3 modeling choice** (e.g. predicting the BOLD window that
follows a thought onset, or deconvolving to estimate neural onset). It is never done
silently in the loader, so the raw temporal relationship stays auditable.

## Boundary / edge cases

- **End-of-run thoughts:** the last thought of sub-001 ends at ~610.6 s, **~10 s past**
  the 600 s BOLD end. `check_within_run(run, tol_s=15)` flags thoughts that *start*
  after the run (none in the subset); thoughts that merely *extend* past the end are
  clipped to the last volume by `bold_window_for_event` (via `time_to_volume` clipping).
- **Silent gaps:** inter-thought intervals with no speech are returned by
  `verbal_gaps()`; they are legitimate (pauses), not errors.
- **Word-level:** not available — alignment is sentence/thought-level only.

## Reliability for prospective prediction

- Onsets are strictly monotonic and non-overlapping in the subset (verified by tests),
  so thought `N+1` is a clean, well-ordered target after thought `N`.
- Sentence-level granularity is sufficient for "next thought" targeting; sub-sentence
  (word) timing is not available.
- The usable BOLD is MNI-space fMRIPrep preprocessed (1.5 s, 400 vols); raw native BOLD
  is not in public S3 (see `ds006067_audit.md`).
