# Repository Architecture

**Status:** canonical · **Baseline:** CM-REPO professionalization
**Companion:** [dependency_boundaries.md](dependency_boundaries.md)

This document describes *how the repository is organized* and *why*, so a new
researcher can navigate it without tribal knowledge. It is not a protocol or a
results document — for those see `docs/protocol/` and `reports/`.

## One-paragraph summary

Causal Mind is a computational cognitive-science / ML research repository. The
importable library lives in `src/causal_mind/` (a layered package); one-off and
reproducible experiment scripts live in `data/scripts/`; frozen scientific
artifacts, manifests, and registries live in `artifacts/`, `data/manifests/`,
and `registries/`; human-readable results and audits live in `reports/` and
`docs/`. The `cm` CLI (`src/causal_mind/cli.py` + `cli_research.py`) is the
single operational entry point for both orchestration and research validation.
Reproducibility is enforced by frozen configs, SHA-256 artifact registries,
invariant tests, a leakage scanner, and a one-command validation script.

## Top-level layout

| Path | Purpose |
|------|---------|
| `src/causal_mind/` | The importable library (layered; see dependency_boundaries.md). |
| `data/scripts/` | Experiment scripts (CM-2…CM-8, deep-dive). Reuse library code; write reports. |
| `data/manifests/` | Frozen split/protocol seals (source of truth for splits). |
| `data/derived/`, `data/raw/` | Derived thought events; raw dataset pointers (data itself is gitignored). |
| `artifacts/` | Frozen model/config artifacts (SHA-256 registered). |
| `registries/` | Artifact, experiment, and lineage registries (JSON, frozen). |
| `claims/` | Claim registry (`claims.json`) with levels 0-8. |
| `experiments/` | Experiment registry. |
| `reports/` | Result reports, audits, scorecards (one dir per workstream). |
| `docs/` | Protocols, ADRs, runbooks, theory, governance, architecture. |
| `tests/` | pytest suite (per-CM-phase + invariants + security + boundaries). |
| `scripts/` | Operational shell: bootstrap, validation, disaster recovery, hooks. |
| `configs/` | Non-frozen config templates. |
| `papers/` | Paper drafts. |
| `orchestration/` | Agent task queue state (runtime; mostly gitignored). |

## The library: `src/causal_mind/`

The library is organized in **layers** (enforced by
`tests/test_import_boundaries.py`). Lower layers never import higher layers.

- **L0 foundation** — `paths` (repo-root discovery, no hard-coded pod paths),
  `exit_codes` (stable CLI exit-code contract), `errors` (domain error
  taxonomy), `runid` (traceable run IDs), `logging_setup` (structured logging),
  `constants` (scientific constants read from frozen configs), `human_data_guard`
  (hard-fail on staged human data), `utils` (dependency-free helpers, e.g. `metrics`).
- **L1 domain** — self-contained scientific modules: `thought` (state + encoding),
  `data` (dataset loaders), `causal` (SCM, identifiability, predicted basin),
  `oracle`, `sim`, `privacy`, `language`, `representations`, `preprocessing`,
  `counterfactual`, `visualization`, `monitoring`, `security`.
- **L2 modeling** — `forecast` (baselines B0-B7, models), `engine`.
- **L3 evaluation** — `eval` (frozen protocol, analyses), `neural`.
- **L4 orchestration** — `orchestrator` (task queue, coordinator, Qwen client,
  review), `agent` (agent loop, sandboxed tools).
- **L5 entry** — `cli` (orchestrator commands), `cli_research` (research
  commands: validate/doctor/claims/artifacts/security/demo/reproduce).

### Key design decisions

1. **Frozen configs are the single source of truth for science.** `constants.py`
   *reads* alpha, basin_tail, horizons, h*, k, split seeds, and encoder/dim from
   the frozen files (`artifacts/cm8_forecaster/config.json`,
   `data/manifests/cm2_split_seal.json`, `data/manifests/cm3_protocol_seal.json`).
   Code never re-hard-codes them; a missing/malformed frozen file raises
   `NotFoundError`/`DataIntegrityError` rather than substituting a default.
2. **No hard-coded absolute paths.** `paths.py` discovers the repo root by
   walking up to `pyproject.toml`, overridable via `CM_REPO_ROOT`/`CM_DATA_ROOT`.
3. **Stable failure semantics.** Domain errors (`errors.py`) carry a machine
   `code` and a mapped exit code (`exit_codes.py`), so CI and the CLI branch on
   stable values, not message text.
4. **Human data is gated.** `human_data_guard.py` hard-fails (pre-commit + CI)
   if real participant data is staged before the human/ethics gate is passed.
5. **Reproducibility is enforced, not assumed.** Frozen artifacts are SHA-256
   registered; invariants, the leakage scanner, and the secret scan run in
   `scripts/validate_project.sh` and `cm validate`.

## Data flow (a typical experiment)

```
raw dataset (gitignored)
  -> data/scripts/build_*  (normalize)  -> data/derived/thought_events/
  -> src/causal_mind.thought (state + frozen encoders)
  -> src/causal_mind.forecast / .eval (model + frozen protocol)
  -> data/scripts/cm_*  (run, write report)  -> reports/<workstream>/
  -> claims/claims.json (claim, level 0-8)  -> registries/ (lineage)
```

Every run should carry a run ID (`runid.make_run_id`) written into its output
manifest so any artifact traces back to (git SHA, timestamp, seed).

## How to navigate

- **I want to run the project health check:** `cm doctor`, then `cm validate`.
- **I want to see current scientific state:** `docs/current_state.md`,
  `reports/cm_lab_scorecard.md`, `claims/claims.json`.
- **I want to add a new experiment:** `docs/runbooks/new_experiment.md`.
- **I want to understand a protocol:** `docs/protocol/` (frozen) +
  `docs/decisions/` (ADRs).
- **I want the glossary:** `docs/glossary.md`.

## What is intentionally NOT here

- No real human participant data (gated; see `docs/governance/`).
- No Kubernetes/Run:ai credentials or tunnel configs (out of scope, read-only).
- No system-level caches (those live on the project PVC, gitignored).
