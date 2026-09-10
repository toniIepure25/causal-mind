# Data

Raw data is **never** committed to git. All data lives on the pod PVC.

```
/home/jovyan/work/causal-mind-v2/data/
  raw/          downloaded dataset files (git-ignored)
  derivatives/  processed features, parcellations, embeddings (git-ignored)
  cache/        encoder caches, HF caches (git-ignored)
  manifests/    dataset manifests: file lists, SHA-256, versions (COMMITTED)
```

## Manifests

Each dataset gets `data/manifests/<dataset>.yaml`:

```yaml
dataset: ds006067
source: https://openneuro.org/datasets/ds006067
version: "<revision or download date>"
license: "<recorded>"
acquired: "<iso date>"
files:
  - path: raw/ds006067/...
    sha256: "<hash>"
    bytes: 123
notes: |
  <audit notes: subjects, runs, TR, transcript format, ...>
```

## Cache keying

Expensive transformations (embeddings, parcellations) are cached under `data/cache/`
keyed by `dataset version + preprocessing config hash + code version`. A cache entry is
only reused if all three match; otherwise it is rebuilt.

## Deletion policy

Never delete raw data unless it is explicitly known to be redownloadable (manifest +
checksums present) and the deletion is recorded in the research log.
