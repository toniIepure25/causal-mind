# CAUSAL MIND

**A Causal World Model for Forecasting and Redirecting Human Thought.**

Core scientific question:

> Can we reconstruct the causal genealogy of human thought, forecast its possible futures,
> and determine whether deliberate or external intervention can causally redirect a
> predicted cognitive trajectory?

Ultimate question:

> When a mind is shown its predicted future and attempts to escape it, does it create a
> genuinely new trajectory — or does that act of escape itself become another predictable cause?

Research program:

```
OBSERVE -> REPRESENT -> FORECAST -> EXPLAIN -> INTERVENE -> REDIRECT -> PREDICT THE ESCAPE
```

Target object:

```
p(Z_future | causal_history, brain_history, thought_history, context, interventions, revealed_predictions)
```

where `Z` is a latent cognitive/thought state.

## Current stage

Phase 0/1 — infrastructure established, epistemic seal being frozen, dataset audit in progress.
See `docs/current_state.md` for the live status, `docs/research_log.md` for the chronology.

## Repository layout

```
causal-mind/
├── docs/            vision, questions, hypotheses, protocol, claims, ADRs, runbooks
├── configs/         data / models / experiments / compute configuration
├── data/            manifests only (raw data lives outside git, on the pod PVC)
├── src/causal_mind/ python package: data, representations, forecasting, causal, agent, orchestrator
├── scripts/         agent supervisor, Qwen tunnel, smoke tests
├── experiments/     experiment definitions and manifests
├── reports/         agent reports, reviews, syntheses
├── tests/           pytest suite (queue, splits, agent loop, security)
├── artifacts/       git-ignored experiment artifacts
└── orchestration/   task queue state, worker state, orchestrator logs
```

## Compute environment

- Pod: `orchestraiq-jupyter` (Kubernetes namespace `runai-romania-dev`), user `jovyan`.
- GPU: 1x NVIDIA A100-SXM4-40GB, CUDA 12.8 driver, PyTorch cu128.
- Persistent storage: NFS PVC at `/home/jovyan/work` (100+ TB free).
- Project root on pod: `/home/jovyan/work/causal-mind`.
- LLM endpoint: `Qwen/Qwen3.8-27B-FP8` via local OpenAI-compatible port-forward at
  `http://127.0.0.1:18000/v1` (Run:ai workload `qwen38-27b12`, see
  `docs/runbooks/qwen_tunnel.md`).

## Agent operation

Six autonomous roles share one Qwen endpoint and one central task queue:

| role | worktree | responsibility |
| --- | --- | --- |
| orchestrator | (base repo) | task DAG, gates, merges, claims registry |
| researcher | `worktrees/causal-mind/researcher` | literature, dataset audits, novelty matrix |
| data | `worktrees/causal-mind/data` | acquisition, manifests, loaders, alignment |
| forecasting | `worktrees/causal-mind/forecasting` | thought state, baselines, temporal models |
| causal | `worktrees/causal-mind/causal` | DAGs, identification, statistics, power |
| reviewer | `worktrees/causal-mind/reviewer` | red team, leakage audits, BLOCK authority |

```bash
scripts/qwen_tunnel_supervisor.sh start          # bring up the Qwen endpoint
scripts/cm-agent-supervisor start                # start all six worker supervisors
scripts/cm-agent-supervisor status
python -m causal_mind.cli status
```

## Validation policy (non-negotiable)

1. Subject-disjoint validation by default; never random row splits.
2. Frozen primary evaluation protocol before touching final test outcomes.
3. Uncertainty always reported (bootstrap CIs, permutation tests, effect sizes).
4. Negative controls and label/permutation controls for every headline result.
5. Claims are registered at an explicit level (0-8); a Level 2 result is never worded as
   Level 6. See `docs/claims_registry.md`.

## Reproducibility

Every experiment writes a manifest (git SHA, config hash, dataset version, split, seed,
environment) under `experiments/manifests/`. See `docs/validation_protocol.md`.
