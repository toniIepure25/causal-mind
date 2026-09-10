# Experiments

Each experiment has:

- a definition in `configs/experiments/<exp-id>.yaml` (hypothesis, model, split, seed,
  metrics, gates),
- a manifest written at run time in `experiments/manifests/<exp-id>.yaml` (git SHA,
  config, dataset version, split, seed, environment, metrics, wall time, audit status),
- outputs under `experiments/outputs/<exp-id>/` (git-ignored).

An experiment is only reported after its manifest exists and the reviewer audit status
is `pass`.
