# Data Smoke: ds006067 Pre-Download Audit

Purpose: minimal audit steps for OpenNeuro ds006067 **before any download**.
This step performs no downloads; it reads only public metadata (openneuro.org
dataset page, README, BIDS sidecars).

## 1. Metadata to verify

1. **Subjects**: count and subject IDs (required for subject-disjoint splits).
2. **Runs**: sessions/runs per subject; session identity noted as confound.
3. **fMRI**: TR, sequence, BIDS validity of the layout.
4. **Transcript format**: file format/encoding, one transcript per run.
5. **Word timestamps**: present, time base (seconds from run start), alignment
   to fMRI time zero.
6. **Thought boundaries**: explicit annotations or derivable from pauses.
7. **Annotations**: cognitive dimensions, provenance, per-run coverage.
8. **License**: research-use compatible; record exact license.
9. **Version**: dataset version/DOI and release date.

## 2. Manifest requirements

`data/manifests/ds006067.yaml` must record:

- dataset ID, version, DOI, license
- per file: relative path, SHA-256, size in bytes
- total footprint (bytes)
- subject/run inventory
- audit date, auditor, source URLs
- audit status: `pending` -> `verified`

Nothing is trusted until the manifest exists with checksums (see
`docs/datasets.md`).

## 3. Minimal-subset download policy

- Download only after the audit above passes.
- Subset: 1-2 subjects, 1 run each.
- Only files needed to validate the loader: BIDS fMRI for those runs plus
  matching transcript, word timestamps, and annotations.
- Record every downloaded file in the manifest with SHA-256 before use.
- Expand the subset only after GATE A (data integrity) passes.
