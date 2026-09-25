# Dependency Boundaries

**Status:** canonical · **Enforced by:** `tests/test_import_boundaries.py`

The `src/causal_mind` package is organized into layers. The rule is simple and
machine-enforced:

> **A module may import from the same or a lower layer, never from a strictly
> higher layer. No two packages may import each other (no 2-cycles).**

This keeps the scientific core (L0-L3) independent of orchestration and CLI
code (L4-L5), keeps the graph acyclic, and makes the architecture reviewable.

## Layers

| Layer | Name | Modules | May import |
|-------|------|---------|------------|
| L0 | foundation | `paths`, `exit_codes`, `runid`, `logging_setup`, `errors`, `constants`, `human_data_guard`, `utils` | L0 |
| L1 | domain | `causal`, `thought`, `data`, `oracle`, `sim`, `privacy`, `language`, `representations`, `preprocessing`, `counterfactual`, `visualization`, `monitoring`, `security` | L0, L1 |
| L2 | modeling | `forecast`, `engine` | L0, L1, L2 |
| L3 | evaluation | `eval`, `neural` | L0-L3 |
| L4 | orchestration | `orchestrator`, `agent` | L0-L4 |
| L5 | entry | `cli`, `cli_research` | L0-L5 |

## Current dependency edges (observed)

```
cli            -> agent, orchestrator
cli_research   -> exit_codes, logging_setup
agent          -> orchestrator
orchestrator   -> monitoring
neural         -> eval
eval           -> forecast, thought, utils
forecast       -> thought, utils
engine         -> causal
constants      -> errors, paths
human_data_guard -> errors, paths
errors         -> exit_codes
(data/thought/causal/...) -> paths, errors   (L1 -> L0)
```

No edge points upward; no 2-cycle exists.

## The eval/forecast boundary (historical cycle, now broken)

`eval/analyses.py` needs `forecast.baselines.{Prediction, TrainCorpus}`
(dataclasses), and `forecast/baselines.py` needs a cosine-similarity helper.
Previously `cosines` lived in `eval/protocol.py`, creating an `eval <-> forecast`
cycle. It was moved to the dependency-free `utils/metrics.py` (CM-REPO S3);
`eval/protocol.py` re-exports it for back-compat. The edge is now one-directional:
`eval -> forecast -> utils`.

## Adding a new module

1. Decide its layer (what does it depend on? what should depend on it?).
2. Add it to the `LAYER` dict in `tests/test_import_boundaries.py`.
3. If it depends on a higher layer, the test fails — either re-layer or move the
   shared dependency down.

The test also fails if a module is *missing* from the `LAYER` dict, so the
boundary is self-maintaining: you cannot add a module without declaring where it
sits.

## Rationale

- **Scientific core stays pure.** L0-L3 (the science) never reach into
  orchestration/CLI, so the science is testable and reusable without the
  agent/Qwen runtime.
- **No cycles.** Cycles hide coupling and make refactoring and review hard.
- **Explicit over implicit.** Every module's layer is declared, so the
  architecture is a reviewable artifact, not folklore.
