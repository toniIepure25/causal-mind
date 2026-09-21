# Validation Profiles & Recovery Runbook (CM-LAB S13, S14)

## Validation profiles (S13)
Three profiles, from fastest (pre-commit) to fullest (disaster recovery). All are
deterministic and require no secrets or datasets.

| profile | command | what it runs | when |
| --- | --- | --- | --- |
| **fast** | `bash scripts/validate_project.sh --fast` | lint/type ratchet, invariants, claims graph, registry integrity, claim linter, security audit, secret scan (no full test suite) | pre-commit / quick gate |
| **full** | `bash scripts/validate_project.sh` | fast + the full pytest suite (173 tests) | every local change, CI |
| **disaster** | `bash scripts/disaster_recovery.sh` | fresh clone -> bootstrap -> full validation -> frozen-artifact integrity | recovery / release sign-off |

CI (`.github/workflows/ci.yml`) runs the **full** profile on every push/PR.

### What the full profile checks
1. **lint/type ratchet** (`cm_lab_lint_gate.py`) — fails only on NEW debt vs the baseline.
2. **tests** — the full pytest suite.
3. **invariants** (`tests/test_invariants.py`) — 10 scientific invariants that must never regress.
4. **claims graph** (`cm_lab_claims_graph.py --check`) — claim DAG schema + traceability.
5. **registry integrity** (`cm_lab_registry.py --check`) — 12 frozen artifacts SHA-unchanged.
6. **claim linter** (`cm_pub_claim_linter.py`) — no BLOCK-level overclaiming language.
7. **security audit** (`cm_lab_security.py --check`) — no secrets/cred-files/public-binds/telemetry.
8. **secret scan** — conservative credential-literal scan.

## Recovery runbook (S14)
Ordered by severity. The authoritative copy is **GitHub** (`toniIepure25/causal-mind`); the
pod repo is the working copy. The frozen release is `cm8-prehuman-v1.0` (immutable).

### R1 — Environment lost (pod recreated, venv gone)  [the weakness that motivated CM-LAB]
```
cd /home/jovyan/work/causal-mind-v2
bash scripts/bootstrap_environment.sh     # uv sync core+dev+neural from uv.lock
bash scripts/validate_project.sh          # confirm green
```
The repo (code + `uv.lock` + configs + frozen artifacts) is self-sufficient; no manual
dependency installation is needed. This is exactly what `scripts/disaster_recovery.sh`
automates end-to-end.

### R2 — Working pod repo lost, GitHub intact
```
git clone https://github.com/toniIepure25/causal-mind.git   # on a machine with access
bash scripts/bootstrap_environment.sh
bash scripts/validate_project.sh
```
CI already confirms this path works (it clones from GitHub on every push).

### R3 — Suspected drift of a frozen artifact
```
.venv/bin/python data/scripts/cm_lab_registry.py --check    # SHA registry
.venv/bin/python data/scripts/cm_lab_claims_graph.py --check  # claim traceability
```
If a frozen artifact's SHA changed, do NOT proceed — restore it from the `cm8-prehuman-v1.0`
tag and re-run validation. Frozen artifacts must never silently change.

### R4 — Lint/type debt regressed
```
.venv/bin/python data/scripts/cm_lab_lint_gate.py           # see the count vs baseline
# fix the new violations, then:
.venv/bin/python data/scripts/cm_lab_lint_gate.py --rebaseline   # lower the bar
```

### R5 — New collaborator onboarding
```
git clone <repo>
bash scripts/bootstrap_environment.sh
bash scripts/validate_project.sh
# read: README.md, docs/current_state.md, docs/claims_registry.md, docs/security_standards.md
```

### What is NOT recoverable from the repo alone
- The large RAW datasets (ds006067 fMRI, etc.) live on the PVC, not in git. The FROZEN
  results, configs, manifests, and reports ARE in the repo, so the scientific record is
  fully recoverable; re-acquiring raw data requires the original sources (OpenNeuro/OSF).
