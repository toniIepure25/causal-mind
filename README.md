# CAUSAL MIND

**A Causal World Model for Forecasting and Redirecting Human Thought.**

**State:** `CMLAB_SCIENTIFIC_DEEP_DIVE_COMPLETE` · **Pre-human freeze:**
`cm8-prehuman-v1.0` (git `8a9d5dd`, 2026-09-20) · **No human data collected.**

Core scientific question:

> Can we reconstruct the causal genealogy of human thought, forecast its possible futures,
> and determine whether deliberate or external intervention can causally redirect a
> predicted cognitive trajectory?

Ultimate question:

> When a mind is shown its predicted future and attempts to escape it, does it create a
> genuinely new trajectory — or does that act of escape itself become another predictable
> cause?

Research program:

```
OBSERVE -> REPRESENT -> FORECAST -> EXPLAIN -> INTERVENE -> REDIRECT -> PREDICT THE ESCAPE
```

Target object:

```
p(Z_future | causal_history, brain_history, thought_history, context, interventions, revealed_predictions)
```

where `Z` is a latent cognitive/thought state.

## Current state (one line per phase)

| phase | state | result |
| --- | --- | --- |
| CM-1 data integrity | `CM1_PASS` | 118 subjects; 10/10 integrity checks |
| CM-2 next-thought prediction | `CM2_PASS` | held-out semantic cosine 0.362 [0.352, 0.372], above all 8 baselines |
| CM-3 multi-horizon | `CM3_PASS` | beats the strongest baseline at every horizon h=1..10 (smooth decay) |
| CM-5 neural incremental value | `CM5_NULL` | no incremental value (gain −0.088, all subjects negative) |
| CM-6 causal identification | `CM6_OBSERVATIONAL_ONLY_NO_IDENTIFICATION` | 0/84 edges identifiable |
| CM-7 public intervention method | `CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT` | ATE −0.039, p=0.073 (method validated; null effect) |
| CM-8 Pre-Oracle / Break-the-Chain | `CM8_CONFIRMATORY_INTACT` | frozen protocol v1.0; no-drift verified; ethics package ready |
| CM-8R pre-human hardening | `CM8R_PREHUMAN_HARDENED` | 10/10 gates; frozen reproducible forecaster |
| CM-9A synthetic Oracle lab | `CM9A_SYNTHETIC_ORACLE_READY` | 4 conditions × 11 policies; RPR/PIE |
| CM-LAB scientific deep dive | `CMLAB_SCIENTIFIC_DEEP_DIVE_COMPLETE` | 9 workstreams; see below |

**CM-LAB deep-dive decisions** (cross-validated, leakage-audited; see
`reports/cm_lab_science_deep_dive.md`):

- `CMXVAL_PARTIAL_REPLICATION` — the effect partially replicates on held-out external
  datasets (survey + OpenPlay); not a universal law.
- `CMUNC_WEAK` — uncertainty estimates are weakly calibrated.
- `CMREP_PARTIAL` — richer representations give partial, not decisive, gains.
- `CMPERS_NULL` — no measurable personalization benefit.
- `CMDYN_LINEAR_PREDICTION_DOMINANT` — dynamics are dominated by linear prediction, not
  nonlinear structure.
- `CMERR_WEAKLY_PREDICTABLE` — large forecast errors are weakly predictable (novelty-driven).
- `CMORACLE_SELECTIVE_ONLY` — oracle selective prediction helps only on the top-decile of
  confident samples; recursion degrades.
- `CMLEAK_PASS` — leakage scanner clean across the deep-dive pipeline.
- `CMLAB_DISASTER_RECOVERY_REPRODUCED` — clean-room disaster recovery reproduced.

The program has moved from **FORECAST** to **EXPLAIN/INTERVENE**. The only remaining
blockers to human data are external: supervisor sign-off, ethics approval, and the pilot.
See `docs/current_state.md` for the live status and `docs/research_log.md` for the
chronology.

## Where to start

- **New collaborator / maintainer:** `docs/runbooks/maintainer.md`
- **Supervisor:** `docs/supervisor/START_HERE.md`
- **Architecture:** `docs/architecture/repository_architecture.md`
- **Master summary:** `docs/CAUSAL_MIND_master_summary.md`
- **Glossary:** `docs/glossary.md` · **Docs index:** `docs/README.md`
- **Pre-human freeze + hashes:** `docs/releases/cm8_prehuman_v1.md`
- **Claim-level evidence:** `docs/claims/evidence_matrix.md`
- **Papers:** `papers/paper1_predictive_dynamics/`, `papers/paper2_prediction_to_intervention/`,
  `papers/paper3_break_the_chain_protocol/`
- **Ethics package:** `docs/ethics/`

## Quick start (reproduction)

```bash
# on the pod, via SSH as jovyan
cd /home/jovyan/work/causal-mind-v2
export HF_HOME=/home/jovyan/work/.hf-home

# 1. Is the environment healthy? (deps, paths, frozen configs, human-data guard)
cm doctor

# 2. Is the project scientifically intact? (lint, invariants, claims, registry,
#    security audit, human-data guard)
cm validate

# 3. Verify the frozen forecaster + clean-room bit-identical re-fit
.venv/bin/python data/scripts/cm8r_cleanroom.py

# 4. Full one-command validation (lint + tests + invariants + registries + scans)
bash scripts/validate_project.sh
```

No network access is required at inference (frozen local artifacts). Exact per-result
commands are in `docs/claims/evidence_matrix.md` and the reproducibility traceability table.

## The `cm` CLI

The single operational entry point (`pyproject.toml` → `cm = "causal_mind.cli:main"`).

**Research commands** (`cm --help`):

| command | what it does |
| --- | --- |
| `cm doctor` | environment/dependency/path/data diagnostics |
| `cm validate [--with-tests]` | scientific-integrity gates (lint, invariants, claims, registry, security, human-data guard) |
| `cm claims verify` | claim registry schema + traceability |
| `cm artifacts verify` | frozen-artifact SHA-256 integrity |
| `cm security scan` | security audit + secret scan + human-data guard |
| `cm demo` | fast demo pipeline |
| `cm reproduce <name>` | named reproduction (`cm8`, `deep-dive`, `leakage`, …) |

**Orchestration commands:** `cm status`, `cm task …`, `cm agent …`, `cm coordinator …`,
`cm review …`, `cm qwen`.

Exit codes are stable and documented (`src/causal_mind/exit_codes.py`); `0` is success.

## Repository layout

```
causal-mind-v2/
├── docs/            architecture, protocol, claims, ethics, runbooks, governance, theory
├── configs/         data / models / experiments / compute configuration
├── data/            manifests (seals, randomization, freeze); scripts (cm2..cm9a, cm8r_*, deep-dive)
├── src/causal_mind/ layered python package (foundation -> domain -> modeling -> eval -> orchestration -> CLI)
├── scripts/         bootstrap, one-command validation, disaster recovery, git hooks
├── reports/         committed results (cm2..cm9a, cm8r_*, deep-dive) + audits + scorecards
├── papers/          paper drafts (paper1..3, oracle theory)
├── tests/           pytest suite (per-phase + invariants + security + import boundaries)
├── artifacts/       frozen experiment artifacts (forecaster, SHA-verified)
├── registries/      artifact / experiment / lineage registries (frozen JSON)
├── claims/          claim registry (claims.json, levels 0-8)
└── orchestration/   task queue state, worker state, orchestrator logs
```

## Architecture

The library is layered and the boundaries are machine-enforced
(`tests/test_import_boundaries.py`): foundation → domain → modeling → evaluation →
orchestration → CLI. Lower layers never import higher layers. See
`docs/architecture/repository_architecture.md` and
`docs/architecture/dependency_boundaries.md`.

## Compute environment

- Pod: `orchestraiq-jupyter` (Kubernetes namespace `runai-romania-dev`), user `jovyan`.
- GPU: 1x NVIDIA A100-SXM4-40GB, CUDA 12.8 driver, PyTorch cu128.
- Persistent storage: NFS PVC at `/home/jovyan/work`.
- Project root on pod: `/home/jovyan/work/causal-mind-v2` (worktrees under
  `/home/jovyan/work/worktrees/causal-mind-v2/`).
- LLM endpoint: `Qwen/Qwen3.8-27B-FP8` via local OpenAI-compatible port-forward at
  `http://127.0.0.1:18000/v1` (see `docs/runbooks/qwen_tunnel.md`). **Not used at
  participant-facing inference** (the CM-8 engine is offline).

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

## Validation policy (non-negotiable)

1. Subject-disjoint validation by default; never random row splits.
2. Frozen primary evaluation protocol before touching final test outcomes.
3. Uncertainty always reported (bootstrap CIs, permutation tests, effect sizes).
4. Negative controls and label/permutation controls for every headline result.
5. Claims are registered at an explicit level (0–8); a lower-level result is never worded as
   a higher-level one. See `docs/claims_registry.md`.
6. The reviewer's leakage audit must pass before any result is reported as validated.

## Key results (exact values)

- **CM-2 (L3):** held-out semantic cosine **0.3623 [0.3523, 0.3720]** vs strongest baseline
  **0.3167 [0.3078, 0.3250]**; permutation p=0.0000; 83/18/17 sealed.
- **CM-3 (L5):** gain over the strongest baseline, h=1 +0.0349 [0.0253, 0.0445] → h=10
  +0.0044 (all CIs exclude 0); smooth monotonic decay; TPH_semantic ≥ ~10 thoughts.
- **CM-5 (L5, null):** N2/Schaefer-400 gain −0.088/−0.085/−0.085/−0.090 (h=1/3/5/10);
  0/16 subjects positive; p=1.0.
- **CM-6 (L5, negative ID):** 0/84 candidate edges identifiable (unmeasured confounding).
- **CM-7 (L6, method validated; null effect):** ATE −0.0386; 2-phase perm p=0.0733; list CI
  [−0.079, 0.002]; integrity 3328/3330; leakage PASS.
- **CM-8R (L0):** clean-room bit-identical; BRP_control 0.0785 ≈ 0.10; chaos 7/7; privacy
  12/12; 10/10 gates.

## Ethics and privacy

- University-of-Vienna ethics package in `docs/ethics/` (frozen protocol v1.0, participant
  information + consent, GDPR data-protection plan, risk assessment, debrief, prereg,
  software-freeze manifest, dry run ALL PASS).
- **Privacy-by-design:** no raw thought text leaves the machine; embeddings only;
  pseudonymized; encryption at rest; no remote LLM/telemetry.
- **Human-data gate:** no real participant data may enter Git before the human/ethics gate
  is passed; enforced by the pre-commit hook and CI (`cm security scan`).
- **Submission authority:** for a Master's thesis, the supervisor / responsible study-law
  body submits (the researcher prepares, does not submit).

## What we are NOT claiming

- No free-will claim (proven or disproven).
- No causal claim from the observational data (0/84 edges identifiable).
- No claim that the (null) public-intervention effect is real.
- The prediction effects are modest; the test set is small (n=17).

## Governance & professionalization

- **Security:** `SECURITY.md` · **Data classification:** `docs/governance/data_classification.md`
- **Versioning & releases:** `docs/governance/versioning.md`, `docs/governance/release_process.md`
- **Runbooks:** `docs/runbooks/` (maintainer, new dataset/experiment/claim, protocol amendment)
- **Threat models:** `docs/governance/threat_models.md`
- **Changelog:** `CHANGELOG.md`

## Citation

See `CITATION.cff`. The pre-human freeze is `cm8-prehuman-v1.0` (git `8a9d5dd`).

## License

See `docs/science/license_data_use_audit.md` for the code license and data-use terms.
Public datasets are cited by their own licenses (OSF `a56rm`; ds005494 CC0).
