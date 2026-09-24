# CM-LAB Disaster Recovery — Second Independent Run (CM-LAB §60)

**Decision:** `CMLAB_DISASTER_RECOVERY_REPRODUCED`
**Script:** `scripts/disaster_recovery.sh`
**Date:** 2026-09-24
**Run by:** orchestrator (second independent run; the first was the prior CM-LAB phase)

## Result

`DISASTER RECOVERY: PASS` — the git repo alone rebuilds a validated, scientifically-consistent
environment:

1. **Fresh clone** (repo is the only surviving artifact) — PASS.
2. **Bootstrap environment** (core + dev + neural, `uv sync`) — PASS.
3. **One-command validation** (`scripts/validate_project.sh`: lint ratchet + tests + invariants
   + registries + claim linter + secret scan) — PASS (all checks green).
4. **Frozen-artifact integrity** (`cm_lab_registry.py --check`) — PASS (12 frozen artifacts
   unchanged, including the `cm8-prehuman-v1.0` release and the frozen CM-8 confirmatory
   protocol v1.0).

## Fix required for this run (and why the first run's assumption was fragile)

The NFS maps the repo to `nobody`, so git's `safe.directory` guard triggers. The original script
relied on `GIT_CONFIG_COUNT/KEY/VALUE` env vars plus `git -c safe.directory=*`. This is **not
sufficient** for a *local* clone: git's `safe.directory` is only honored from **protected
(system/global) config** — not from `-c` or env vars — and a local `git clone` spawns a
`git-upload-pack` subprocess that must also see the setting. On this pod the global config's
`safe.directory` listed only two unrelated repos, so the clone failed with "dubious ownership".

**Fix:** the script now creates a temp `HOME` with a `.gitconfig` containing
`[safe] directory = *` and exports it for the whole run, so every git subprocess (including the
clone's `git-upload-pack`) honors it. The temp `HOME` is removed on exit. This makes the test
self-sufficient and independent of the ambient global git config.

## Guardrails

- Read-only with respect to frozen artifacts (the integrity check verifies, not modifies).
- The temp work + temp `HOME` dirs are removed on exit.
- No human data. No CM-8 change.
