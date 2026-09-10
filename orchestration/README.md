# Orchestration

Filesystem state for the multi-agent system.

```
orchestration/
  tasks/        central task queue (COMMITTED): queue/ running/ review/ done/ blocked/ killed/
  state/        orchestrator loop state (git-ignored)
  workers/      per-worker runtime state (git-ignored)
  logs/         supervisor and agent logs (git-ignored)
  decisions/    orchestrator gate decisions (COMMITTED)
```

Task files are YAML (`causal_mind.orchestrator.models.TaskSpec`). Transitions between
states are atomic file renames; a task in exactly one state directory at a time.
Claim = rename from `queue/` to `running/`; a lost race simply finds the file gone.

Gate decisions (KEEP / ITERATE / KILL per research loop) are written to `decisions/`
and summarized in `docs/current_state.md`.
