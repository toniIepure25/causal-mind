# CM-REPO Scorecard

**Date:** 2026-09-25 · **Phase:** Repository Professionalization, Governance &
Research Engineering

## Final state

```
CMREPO_EXPERT_GRADE_READY
```

## Gate results

| Gate | Result |
|------|--------|
| Repository audit (P0-P3) | ✅ done — no P0; P1s are portability, not integrity |
| Architecture + dependency boundaries | ✅ docs + enforced import-boundary test |
| Path management (no hard-coded pod paths in library) | ✅ `paths.py` |
| Centralized scientific constants | ✅ `constants.py` (reads frozen configs) |
| Error taxonomy + exit codes + run IDs + logging | ✅ |
| Research CLI (doctor/validate/claims/artifacts/security/demo/reproduce) | ✅ |
| Human-data guard (pre-commit + CI) | ✅ verified to block staged human data |
| Dead modules removed (with provenance) | ✅ |
| README professionalized | ✅ |
| Governance (versioning, release, data class, env, threat models, SECURITY, CHANGELOG) | ✅ |
| Runbooks (maintainer, new dataset/experiment/claim, protocol amendment) | ✅ |
| Docs index + glossary | ✅ (all links valid) |
| Critical code review | ✅ (1 real bug found + fixed) |
| Project health report | ✅ |
| Full validation | ✅ `cm validate --with-tests` 8/8 + `validate_project.sh` PASS |
| CM-8 freeze intact | ✅ `cm reproduce cm8` + invariants + 12/12 SHA |
| No human data | ✅ guard clean |
| Security scan | ✅ |
| Claim traceability | ✅ |

## Invariants preserved (hard constraints)

- ✅ NO human data collected.
- ✅ NO change to the CM-8 confirmatory protocol (no-drift verified).
- ✅ NO reinterpretation of existing results.
- ✅ NO scientific result shopping.
- ✅ Frozen artifacts unchanged (12/12 SHA-verified).
- ✅ Lint ratchet at baseline (ruff 32/32, mypy 93/93).

## Follow-ups (non-blocking, tracked)

| ID | Sev | Item |
|----|-----|------|
| F2 | P1 | Migrate ~90 `data/scripts/*.py` off hard-coded pod paths to `causal_mind.paths`. |
| F3 | P2 | Auto-discover deep-dive scripts in the leakage scanner (or test the list is complete). |
| F4 | P2 | Make leakage L5 a real per-entry assertion (currently a justified static note). |
| F5 | P2 | Resolve the `None` placeholder `frac_above_marginal` in `eval/analyses.py`. |
| F6 | P3 | Re-verify lineage SHAs in `cm_lab_registry.py --check`. |
| F7 | P3 | Standardize on one RNG library (numpy) across splits/protocol. |

## Verdict

The repository is professional, reproducible, auditable, secure, and
maintainer-ready. It is fit for expert maintenance and for the pre-human freeze
it supports. **`CMREPO_EXPERT_GRADE_READY`.**
