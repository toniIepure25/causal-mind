# CM-LAB Final Report (S92)

**Final state: `CMLAB_PROFESSIONAL_RESEARCH_PLATFORM_READY`**
Date: 2026-09-21 · Base: `cm8-prehuman-v1.0` (git `8a9d5dd`) · Head: see `git log`

## Mission
Turn CAUSAL MIND into a professional, reproducible, portable research operating system with
external validation, pre-pilot integration, and disaster-recovery resilience — while keeping
the `cm8-prehuman-v1.0` freeze and all frozen scientific results immutable.

## What was built (the Research OS)
| section | deliverable | status |
| --- | --- | --- |
| S4 | Reproducible environment: `pyproject.toml` + `uv.lock` + `scripts/bootstrap_environment.sh` | done |
| S6 | One-command validation: `scripts/validate_project.sh` (+ lint/type ratchet gate) | done |
| S7 | Scientific invariant suite: `tests/test_invariants.py` (10 invariants) | done |
| S8 | Claim graph: `claims/claims.json` + `data/scripts/cm_lab_claims_graph.py` | done |
| S9 | Data lineage: `registries/lineage.json` | done |
| S10 | Artifact registry: `registries/artifact_registry.json` (12 frozen SHAs) | done |
| S11 | Experiment registry: `registries/experiment_registry.json` | done |
| S12 | CI pipeline: `.github/workflows/ci.yml` (full validation on push/PR) | done |
| S13/S14 | Validation profiles + recovery runbook: `docs/validation_and_recovery.md` | done |
| S60/61 | Disaster-recovery test: `scripts/disaster_recovery.sh` | done |
| S75-84 | Security audit + standards: `data/scripts/cm_lab_security.py`, `docs/security_standards.md` | done |

Each is wired into the one-command validation and CI, so the platform self-checks on every
change.

## The scientific result (CM-XVAL first milestone, S16/S18-24)
External validation of the CM-2/CM-3 predictive-dynamics finding on an external, domain-shifted
public dataset (**Open Play**, openESM 0075, Zenodo `10.5281/zenodo.17536656`, gaming-diary
free-text `displaced_activity`).

- **Protocol:** faithful CM-3 transfer — subject-disjoint 473/101/102 (fresh seed 20260921),
  frozen MiniLM, k=3 history, horizons h=1..10, baselines B0-B7, subject-level bootstrap CIs,
  target-shuffle permutation. Leakage-audited.
- **Result:** the linear model beats the strongest frozen baseline at **every** horizon
  (gain +0.016..+0.034, all CIs exclude 0) — the "beats-baselines" effect **transfers**.
  But the target-shuffle permutation is not significant (p=0.71): the absolute test cosine
  (~0.64) is dominated by within-person similarity, so the model predicts a *typical* entry
  for the person rather than the *specific* next entry.
- **Decision: `CMXVAL_PARTIAL`** — recorded as **new claim C-101** (L3). The baseline-beating
  signal generalizes; strong temporal-semantic prediction does not fully transfer to short,
  repetitive activity text. An honest boundary-condition finding, not a refutation.

## Target states (all achieved)
- **CMLAB_RESEARCH_OS_PASS** — env + validation + invariants + claim graph + registries + CI.
- **CMLAB_DISASTER_RECOVERY_PASS** — repo alone rebuilds a validated, consistent environment.
- **CMLAB_CLAIM_TRACEABILITY_PASS** — every claim traces to its computation.
- **CMLAB_SECURITY_PASS** — no secrets / cred-files / public binds / telemetry; pinned deps.
- **External-validation decision** — `CMXVAL_PARTIAL` (C-101).

## Constraints honored
- No human data collected.
- Frozen CM-8 confirmatory protocol v1.0 unchanged; `cm8-prehuman-v1.0` immutable (no retag/rewrite).
- C-001..C-012 unchanged; the external result is a NEW claim (C-101).
- No result shopping; the XVAL null/partial is reported honestly.
- No credentials committed; no public service exposure; no Kubernetes/Run:ai mutation.

## Limitations & next steps
1. **Second external domain** — validate on van Halem "Daily event" (openESM 0070) to firm up
   the `CMXVAL_PARTIAL` conclusion (replicate / partial / null).
2. **Uncertainty + dynamics + Oracle theory** (S25-42) — queued scientific deep-dive.
3. **Dependency vuln-DB audit** — run `pip-audit` when a vulnerability feed is reachable.
4. **Pre-pilot** — the CM-8 confirmatory protocol remains frozen and ready for the (human-gated)
   ethics + pilot authorization; nothing here changes that path.

## Reproduction
```
bash scripts/validate_project.sh        # full platform self-check (green)
bash scripts/disaster_recovery.sh       # rebuild-from-repo proof (green)
.venv/bin/python data/scripts/cm_xval_openplay.py   # re-run the XVAL
```
