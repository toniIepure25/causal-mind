# Maintainer Runbook

**Status:** canonical · **Audience:** anyone who merges to `main` or cuts a release.

This is the operating manual for keeping the repository healthy. If you can do
these things, you can maintain Causal Mind.

## First time on a clone

```bash
# 1. Install the environment (mirrors CI): core + dev + neural extras.
bash scripts/bootstrap_environment.sh

# 2. Install the git hooks (human-data guard + lint ratchet on commit).
bash scripts/install_hooks.sh

# 3. Confirm the environment is healthy.
cm doctor

# 4. Confirm the project is scientifically intact.
cm validate --with-tests
```

If `cm doctor` or `cm validate` fails, **stop** and fix the environment before
doing anything else.

## Before you push (every time)

```bash
cm validate --with-tests        # all gates + full test suite
cm security scan                # security + human-data guard (also in pre-commit)
```

The pre-commit hook already runs the human-data guard + lint ratchet on every
commit. CI re-runs the full one-command validation on every push/PR.

## Adding code

1. Follow the [layered architecture](../architecture/dependency_boundaries.md).
   New modules **must** be assigned a layer in
   `tests/test_import_boundaries.py` (the test fails otherwise).
2. No hard-coded absolute paths — use `causal_mind.paths`.
3. No hard-coded scientific constants — read them from `causal_mind.constants`
   (which reads the frozen configs).
4. Raise domain errors (`causal_mind.errors`), not bare `Exception`.
5. Keep the lint ratchet green: `cm validate` (ruff + mypy vs baseline).
6. Add or update tests. Invariant-affecting changes need an invariant test.

## Adding a scientific result

See the [new experiment runbook](new_experiment.md) and the
[new claim runbook](new_claim.md). The non-negotiables:

- Subject-disjoint splits only; frozen protocol before touching test outcomes.
- Report uncertainty (CIs, permutation, effect size) + negative controls.
- Register the claim at an honest level (0-8); the claim linter checks language.
- The reviewer's leakage audit must pass before a result is "validated".

## Cutting a release

See the [release process](../governance/release_process.md). Only the
orchestrator/human cuts and pushes tags.

## When something breaks

| Symptom | First check |
|---------|-------------|
| `cm doctor` FAIL on a dep | `bash scripts/bootstrap_environment.sh` (re-sync `uv`). |
| `cm validate` FAIL on invariants | A frozen protocol/seal changed — run `cm reproduce cm8`; do NOT edit the seal. |
| `cm artifacts verify` FAIL | A frozen artifact changed — restore it or cut a new freeze (never edit in place). |
| Pre-commit blocks a commit | Read the reason (human data? lint debt?). Fix the cause; never `--no-verify` to bypass the human-data guard. |
| Paths look wrong on a new machine | Set `CM_REPO_ROOT`/`CM_DATA_ROOT`; check `cm doctor`. |
| NFS "dubious ownership" git errors | Use `git -c safe.directory=* …` or the temp-`GIT_CONFIG_GLOBAL` pattern (see `scripts/install_hooks.sh`). |

## Disaster recovery

If the working tree or environment is lost, `scripts/disaster_recovery.sh`
rebuilds a clean clone from the git remote + locked environment and verifies it
bit-identically. See `reports/disaster_recovery_second_run.md` for evidence.

## What you must never do

- Force-push or rewrite `main` history.
- Edit a frozen protocol seal or frozen artifact in place.
- Bypass the human-data guard (`--no-verify`) to commit participant data.
- Commit a secret.
- Change a frozen protocol's interpretation without a
  [protocol amendment](protocol_amendment.md).
