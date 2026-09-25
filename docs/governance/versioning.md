# Versioning Policy

**Status:** canonical

## Scheme

The repository uses **semantic versioning** (`MAJOR.MINOR.PATCH`) for the
`causal_mind` package and for tagged releases.

- **MAJOR** — a breaking change to the public API or to a frozen protocol's
  interpretation. Requires an ADR and, if it touches a frozen protocol, a
  [protocol amendment](../runbooks/protocol_amendment.md).
- **MINOR** — a new feature, new experiment, or new capability that does not break
  existing results.
- **PATCH** — a bug fix, refactor, or documentation change with no behavioral
  change to scientific results.

## Frozen releases are immutable

The **pre-human freeze** `cm8-prehuman-v1.0` (git `8a9d5dd`) and any future
`*-v*` freeze tags are **immutable**. A freeze tag points at a commit whose
frozen artifacts (in `registries/artifact_registry.json`) are SHA-256 sealed.
You never modify a frozen release; you cut a new one.

- A freeze tag is created only by the orchestrator/human, after the
  [release process](release_process.md) gates pass.
- Frozen artifacts are verified by `cm artifacts verify` and
  `data/scripts/cm_lab_registry.py --check` (run in CI and `cm validate`).

## What is versioned where

| Artifact | Versioning |
|----------|-----------|
| `causal_mind` package | `pyproject.toml` `[project] version` (semver). |
| Frozen releases | git tags `cm8-prehuman-v1.0`, etc. (immutable). |
| Frozen artifacts | `version` field in `registries/artifact_registry.json` + SHA-256. |
| Protocols | `docs/protocol/*_frozen_protocol.md` (frozen) + amendment series. |
| Claims | `claims/claims.json` (append-only; levels 0-8). |

## Branching and tags

- `main` is the only long-lived branch and is always valid to check out.
- Feature work happens in short-lived branches or git worktrees (see
  [maintainer runbook](../runbooks/maintainer.md)); it is merged to `main` after
  `cm validate` passes and review.
- Release tags are cut from `main` only. No force-push, ever.

## Rules

1. Never rewrite history on `main` (no force-push, no rebase of pushed commits).
2. Every frozen release has a changelog entry and a release-note doc under
   `docs/releases/`.
3. A change that would alter a frozen result is a **protocol amendment**, not a
   version bump — see [protocol amendment runbook](../runbooks/protocol_amendment.md).
4. Bump `pyproject.toml` version and `CHANGELOG.md` in the same commit that
   changes behavior.
