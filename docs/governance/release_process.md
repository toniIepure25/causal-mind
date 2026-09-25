# Release Process

**Status:** canonical · **Companion:** [versioning.md](versioning.md)

A **release** is an immutable, reproducible snapshot of the repository plus its
frozen artifacts. There are two kinds:

1. **Freeze release** (e.g. `cm8-prehuman-v1.0`) — seals a protocol + artifacts
   before a scientific milestone (pre-human, post-human, etc.). Immutable.
2. **Maintenance release** — a semver tag of `main` for collaborators.

## Freeze release checklist

A freeze is cut only when **all** of the following pass. Each maps to a command.

| # | Gate | Command | Must be |
|---|------|---------|---------|
| 1 | One-command validation | `bash scripts/validate_project.sh` | PASS |
| 2 | Research gates | `cm validate --with-tests` | PASS |
| 3 | Environment healthy | `cm doctor` | OK |
| 4 | Frozen-artifact integrity | `cm artifacts verify` | PASS |
| 5 | Claim registry integrity | `cm claims verify` | PASS |
| 6 | Security + human-data guard | `cm security scan` | PASS |
| 7 | Leakage audit (reviewer) | reviewer sign-off in `reports/` | PASS |
| 8 | No human data (pre-human) | `cm security scan` (guard) | clean |
| 9 | CM-8 no-drift (if post-freeze) | `cm reproduce cm8` | PASS |

## Procedure

1. **Prepare.** Ensure `main` is green (`cm validate --with-tests`). Update
   `CHANGELOG.md` and `docs/current_state.md`.
2. **Register artifacts.** Add any new frozen artifacts to
   `registries/artifact_registry.json` with `sha256`, `commit`, `config_hash`,
   `environment_hash`. Verify with `cm artifacts verify`.
3. **Cut the tag.** From a clean `main`:
   ```bash
   git tag -a cm8-prehuman-v1.0 -m "pre-human freeze"
   ```
   (Tags are pushed by the orchestrator/human, never by an agent.)
4. **Write release notes.** Add `docs/releases/<name>.md` with: the tag, the
   commit SHA, the list of frozen artifacts + SHAs, the validation evidence, and
   the exact reproduction commands.
5. **Announce.** Record the release in `docs/current_state.md` and the changelog.

## Rollback

Because releases are immutable tags, "rollback" means checking out an earlier
tag — never rewriting `main`. If a frozen artifact is found to be corrupt, the
response is a **new** freeze with a corrected artifact and a documented
amendment, not a silent re-freeze.

## Who can cut a release

Only the **orchestrator** or a **human** cuts and pushes tags. Worker agents
prepare the release (run the gates, register artifacts, draft notes) but do not
push tags. This matches the global rule: no git push from agents.
