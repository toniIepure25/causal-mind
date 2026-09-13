# CM-5 Access Audit — OpenNeuro ds006067 (fMRIPrep MNI BOLD)

**Date:** 2026-09-13 · **Anchor:** `23d20f1` (frozen CM-3 provenance)
**Goal:** acquire the validated fMRIPrep MNI-space BOLD derivatives + confounds +
metadata for the initial experiment (sub-001, sub-005 first).

## Environment

- Pod: x86_64 Linux, git 2.43.0. **No** git-annex/datalad/node preinstalled;
  **no passwordless sudo** (apt install blocked).
- Installed a **standalone git-annex 10.20260717** (self-contained binary from
  `downloads.kitenet.net`, placed under the PVC at
  `/home/jovyan/work/.local/git-annex/git-annex.linux/`). Works.

## Access methods attempted (all official paths)

| Method | Result | Detail |
|---|---|---|
| OpenNeuro dataset API `api.openneuro.org` | **UNREACHABLE** | no A record from 8.8.8.8 and 1.1.1.1 (raw DNS query). |
| OpenNeuro dataset API `api.neuro.polymtl.ca` | **UNREACHABLE** | no A record from public resolvers. |
| `openneuro.org/api/` | health only | returns `OK`; `/api/datasets/...` → 404 (not the dataset API). |
| OpenNeuro git server `openneuro.org/datasets/ds006067[.git]` | **not git** | `info/refs` returns the React SPA HTML. |
| OpenNeuro annex `openneuro.org/annex/ds006067` | **not git/annex** | all paths return SPA HTML. |
| **GitHub mirror `OpenNeuroDatasets/ds006067`** | **REACHABLE** | shallow clone OK: full BIDS tree, derivatives tree, git-annex pointers + keys. |
| git-annex `get` from OpenNeuro annex | **FAILS** | `Unable to parse git config from .../annex/ds006067/config` (SPA HTML). |
| S3 `openneuro` (public) | old format only | `ds006067/ds006067_R2.0.0/` is **empty** (compressed-tarball era). |
| S3 `openneuro-derivatives` (public) | no ds006067 content | `fmriprep/`,`mriqc/` prefixes exist but no ds006067 objects at expected keys. |
| S3 `openneuro-datasets` | **403 (auth required)** | the git-annex content bucket; objects need signed URLs minted by the (down) API. |

## Conclusion

The BOLD content lives in the `openneuro-datasets` S3 bucket, which requires
signed URLs minted by the OpenNeuro dataset API. **The API is unreachable
(no A record from public DNS) and the git/annex endpoints return the website
SPA, not data.** Therefore the fMRIPrep MNI BOLD cannot be downloaded from the
pod at this time. This is a content-service availability failure, not a
permission or method gap.

## What IS available (data-independent assets)

- **All 118 `events.tsv`** (raw, in git, not annexed): `onset`, `duration`,
  `transcript` in the **MRI time base** (seconds from scan start).
- **`participants.tsv`**: 118 subjects, age, sex.
- **Full BIDS + derivatives tree**: exact file names, git-annex keys, JSON
  metadata pointers for the fMRIPrep 23.2.1 MNI152 derivatives
  (`..._space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz`,
  `..._desc-preproc_smooth4mm_denoise_bold.nii.gz`,
  `..._desc-brain_mask.nii.gz`, `..._desc-confounds_timeseries.tsv`,
  `..._desc-preproc_bold.json`).
- **Alignment validated (partial):** OSF `start_time` is in the MRI time base —
  sub-001 event 0 OSF start 9.59 s = MRI onset 9.59 s; sub-005 12.70 s = 12.70 s;
  transcripts match. OSF thoughts are coarser than the MRI events (different
  segmentation), which is expected and handled by mapping OSF thoughts to BOLD
  volumes via their `[start_time, end_time]`.

## Retry

A background poller re-checks the API DNS + a sample S3 object every few minutes
and logs to `/home/jovyan/work/cm5_access_retry.log`. When the API resolves, the
acquisition script (below) can run immediately.
