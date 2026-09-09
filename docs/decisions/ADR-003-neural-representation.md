# ADR-003: Neural representation ladder

Status: accepted (2026-09-09)

## Context

~100 subjects x fMRI. Full-voxel transformer encoders would be overparameterized and
underdetermined; raw voxel input is also the highest-leakage-risk path.

## Decision

Neural features are introduced in a ladder, each rung validated before the next:

1. **R1 — atlas/parcellation features** (e.g., Schaefer 400 or dataset-native
   parcellation): mean signal per parcel per sample. Default starting point.
2. **R2 — network-level features**: mean over canonical networks (DMN,
   frontoparietal/control, salience, hippocampal/MTL, language/semantic) as
   interpretable aggregates.
3. **R3 — PCA/ICA components** fit on train subjects only.
4. **R4 — ROI embeddings** for a documented ROI set.
5. **R5 — learned spatial encoder** (small CNN/attention over parcels), only if R1-R4
   show the signal is spatially structured beyond parcellation.
6. **R6 — full-brain learned representation** only if R5 is justified and data volume
   supports it.

Rules:

- Preprocessing (denoising, confound regression, normalization) is fit on train
  subjects only and applied identically elsewhere.
- **Lag discipline:** BOLD lags neural activity by ~1-6 s. All neural features used to
  predict `T_{t+1..t+H}` must be lag-audited: the lag grid (e.g., -6..+6 s) is
  pre-registered, and the primary claim uses the hemodynamically defensible lags
  (present or past signal predicting future thought), never future signal.
- The reviewer audits the lag grid and the train/val/test temporal separation
  explicitly for every neural experiment.

## Consequences

- CM-5 (neural incremental value) starts at R1 and only advances rungs on evidence.
- Model sizes stay in the 1e5-1e7 trainable parameter range at this data scale.
