# CM-REPO — Repository Architecture Audit (CM-REPO §1)

**Date:** 2026-09-24 · **Baseline:** git `cf66aeb` · **State:** `CMLAB_SCIENTIFIC_DEEP_DIVE_COMPLETE`
**Scope:** full-repository expert-maintainer audit. No changes made during the audit.

Classification: **P0** scientific/reproducibility/security risk · **P1** major maintainability
risk · **P2** professionalism/developer-experience · **P3** cosmetic/optional.

## Repository shape (observed)

- 602 git-tracked files. Top-level: `src/` (72), `data/` (239, mostly scripts+manifests),
  `docs/` (99), `reports/` (84), `orchestration/` (33), `tests/` (21), `scripts/` (18),
  `configs/` (9), `papers/` (6), `registries/` (4), `artifacts/` (3), `experiments/` (2).
- `src/causal_mind/` is a clean, modular library (~6.9k LOC): `causal`, `forecast`, `thought`,
  `data`, `engine`, `oracle`, `sim`, `privacy`, `neural`, `eval`, `orchestrator`, `agent`,
  `utils`, `security`, `monitoring`, `visualization`, `preprocessing`, `representations`,
  `language`, `counterfactual`, plus `cli.py`.
- `data/scripts/` holds **108 Python scripts** (30 cm5, 16 cm-lab/deep-dive, 13 cm8r, 7 run,
  5 cm8, 5 cm7, 5 cm6, plus scratch).
- Strong existing infrastructure: 4 ADRs (`docs/decisions/`), 2 runbooks (`docs/runbooks/`),
  frozen protocols (`docs/protocol/`), claim registry (`claims/claims.json`), experiment
  registry (`experiments/experiment_registry.json`), 3 registries (`registries/`), 21 test
  files, `cm` CLI (orchestrator-focused), comprehensive `.gitignore`, `uv.lock`, CI
  (`.github/workflows/ci.yml`), `.env.example`.

## Findings

### P0 — scientific / reproducibility / security risk
None blocking. The CM-LAB phase already hardened the repo (frozen artifacts SHA-verified,
leakage scanner, secret scan, invariants, disaster recovery). The items below that touch
reproducibility are classified P1 because the current bootstrap + disaster-recovery path
compensates, but they would break a naive fresh-environment run.

### P1 — major maintainability risk
1. **Hard-coded absolute paths in library code** (`/home/jovyan/...`) in 6 `src/` files:
   `eval/protocol.py` (`SEAL_PATH`), `thought/encode.py` (`HF_HOME`, `TRANSFORMERS_CACHE`,
   `CACHE_DIR`), `data/ds006067.py` (`DEFAULT_DATA_ROOT`), `data/osf_a56rm.py` (`DERIVED`),
   `agent/tools.py` (PATH). 90 `data/scripts/*.py` also hard-code the pod path. Breaks
   portability (§9, §10). The `setdefault` env vars are overridable, but `SEAL_PATH`/`DERIVED`/
   `DEFAULT_DATA_ROOT`/`CACHE_DIR` are not.
2. **Dead / legacy modules.** `src/causal_mind/evaluation/` is empty (5-byte `__init__`);
   `src/causal_mind/forecasting/baselines.py` is an older B0-B5 stub ("Not yet implemented")
   superseded by `forecast/baselines.py`. Neither is imported anywhere (§5).
3. **Script sprawl.** 108 scripts in `data/scripts/` with no separation of reusable logic vs
   one-off runs; reusable scientific logic is duplicated across scripts rather than living in
   `src/` (§5).
4. **No centralized scientific constants.** `alpha`, `basin_tail`, `horizons`, `h*`, `k`,
   split seeds, representation IDs are duplicated as literals across modules/scripts instead of
   being read from the frozen configs (§8).
5. **No domain error taxonomy.** Generic `Exception`/`ValueError`/`RuntimeError` throughout;
   no `ProtocolViolationError`, `ArtifactMismatchError`, `LeakageDetectedError`,
   `FrozenConfigMutationError`, `HumanGateViolationError`, etc. (§13).
6. **No human-data guard.** Nothing hard-fails if a real participant-data file is staged into
   Git (§43). Critical given CM-8 will produce human thought streams.
7. **No run identifiers / exit-code contract / structured logging standard** (§14, §15, §16).
8. **`cm` CLI is orchestrator-only** (status/task/agent/coordinator/review/qwen). No research
   surface: `validate`, `doctor`, `claims verify`, `artifacts verify`, `reproduce`, `demo`,
   `security scan` (§6, §18, §114).
9. **Runtime state tracked in Git:** `.qwen-setup/supervisor.pid` (a PID file) is committed
   (§182). Should be gitignored.

### P2 — professionalism / developer-experience
1. **README state is stale:** header says `CM8R_PREHUMAN_HARDENED`; the accepted state is
   `CMLAB_SCIENTIFIC_DEEP_DIVE_COMPLETE` (§19).
2. **Missing governance docs:** no `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`,
   versioning policy, release process, branching strategy, PR/issue templates (§25-31).
3. **Missing navigation:** no `docs/README.md` index, no `docs/glossary.md` (§81, §82).
4. **Missing runbooks:** only `agent_harness.md` and `qwen_tunnel.md` exist; no
   maintainer / new-dataset / new-experiment / new-claim / protocol-amendment runbooks
   (§123-127).
5. **No `cm doctor`, no project-health report, no quality scorecard** (§18, §116, §117).
6. **No data classification, threat models, env-var registry** beyond a minimal `.env.example`
   (§46, §47, §119-121).
7. **Agent config tracked:** `.opencode/opencode.jsonc` is committed (§184).
8. **Duplicate doc dirs:** `docs/protocol/` and `docs/protocols/` both exist (§79).

### P3 — cosmetic / optional
1. Top-level `*_commit_msg.txt` files (gitignored, present on disk) — workflow scratch.
2. Inconsistent naming (`cm8` vs `cm8r`, `cm` deep-dive prefix) — acceptable historical
   convention, but worth an index.
3. `docs/protocols/cm5_mri_eligibility.md` is the sole occupant of `protocols/` (should merge
   into `protocol/`).

## What is already good (do not regress)
- Frozen-artifact SHA registry + invariants + leakage scanner + secret scan + claim graph
  (all from CM-LAB). Keep and build on.
- `uv.lock` + `bootstrap_environment.sh` + `disaster_recovery.sh` (reproducibility core).
- Clean `src/causal_mind/` module boundaries; `pyproject.toml` with `cm` entry point and
  ruff/mypy/pytest config.
- ADRs, frozen protocols, claim/experiment registries.

## Recommended action order
1. Fix P1 reproducibility (hard-coded paths → project-root discovery + env overrides).
2. Add the research CLI (`cm validate/doctor/claims/artifacts/status/demo/reproduce/security`).
3. Add human-data guard + secret-scan strengthening (security).
4. Centralize constants; add error taxonomy + exit codes + run IDs.
5. Remove/archive dead modules with provenance.
6. Governance + navigation docs (architecture, dependency boundaries, runbooks, glossary,
   index, SECURITY, CHANGELOG, versioning, release process).
7. README rewrite; critical code review; project health; final scorecard.

**No frozen scientific content is modified by any of the above. No human data. No CM-8
protocol change. No reinterpretation of existing results.**
