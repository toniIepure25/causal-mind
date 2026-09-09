# Architecture

## Scientific pipeline

```
OBSERVE          ds006067 transcripts + fMRI (+ EEG later)
   |
REPRESENT        Thought State Z_t = [semantic, topic, temporality, self_relevance,
   |              affect, episodic_memory, goal_directedness, confidence, control,
   |              neural_latent]
   |              each field tagged: observed | annotated | model-derived | latent
   |
FORECAST         p(Z_{t+1..t+H} | history)  -- baselines B0-B5, then sequence models
   |
EXPLAIN          M_language vs M_fusion (neural incremental info);
   |              candidate dynamic SCMs; conditional-independence pruning
   |
INTERVENE        P(future | do(X)) counterfactual engine (identified claims only)
   |
REDIRECT         randomized intervention designs (future human experiments)
   |
PREDICT ESCAPE   p(future | history, prediction_shown, response_policy)
```

## Software layout

```
src/causal_mind/
  data/            dataset clients, manifests, checksums, loaders
  preprocessing/   transcript segmentation, timestamps, fMRI feature extraction
  representations/ Thought State assembly, semantic encoders (frozen), dimensional baselines
  language/        text utilities, embedding caches
  forecasting/     baselines B0-B5, sequence models, multi-step, calibration
  neural/          neural encoders (parcellation -> z_brain), fusion
  causal/          DAGs, SCM specification, conditional independence tests
  counterfactual/  do-calculus simulation (identified claims only)
  evaluation/      metrics, splits, permutation/bootstrap, manifests
  visualization/   predictability curves, reliability diagrams
  agent/           Qwen tool-loop agent harness (tools, loop guards, reports)
  orchestrator/    task queue (atomic claims), coordinator, planner, review, status
  monitoring/      GPU/system snapshots
  security/        credential scanning
  utils/           splits, manifests, io
scripts/           supervisor, tunnel, smoke tests
orchestration/     queue state (git-tracked task YAMLs), worker state, logs
```

## Agent system

```
                    ORCHESTRATOR (base repo)
                        |  task DAG, gates, merges
        ┌───────────┬───┴───────┬────────────┬────────────┐
        v           v            v            v            v
   RESEARCHER    DATA      FORECASTING     CAUSAL       REVIEWER
   (worktree)   (worktree) (worktree)     (worktree)   (worktree)
        |           |            |            |            |
        └───────────┴──────┬─────┴────────────┴────────────┘
                           v
              central task queue (orchestration/tasks)
              atomic claim via file rename; one claim per task
                           v
              Qwen/Qwen3.8-27B-FP8 @ 127.0.0.1:18000 (single shared endpoint)
```

- Each worker runs in its own git worktree/branch; the queue and reports are shared
  from the base repo (env: `CM_QUEUE_ROOT`, `CM_REPORT_ROOT`).
- Workers use the direct Qwen tool loop (`causal_mind.agent`) with a bounded tool
  surface (bash/read/write/edit/grep/glob), workdir jail, deny rules, max action
  cycles, repeated-command detection, and no-progress detection.
- The reviewer role is read-mostly and has BLOCK authority: a result cannot be marked
  validated without a passing leakage audit.
- OpenCode (`.opencode/opencode.jsonc`) remains available for interactive/TUI work
  against the same endpoint.

## Compute strategy

- One A100-40GB: mixed precision, gradient accumulation, memory-mapped fMRI, cached
  frozen embeddings, resumable preprocessing, checkpointing.
- No large trainable LLMs. Frozen pretrained semantic encoders for text.
- Neuro models sized to ~100 subjects (parcellation-level features first, full-brain
  only if warranted).
