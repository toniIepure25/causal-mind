# Project Health Report

**Date:** 2026-09-25 · **Baseline:** CM-REPO professionalization
**Method:** measured metrics + `cm validate --with-tests` (full gate).

## Overall: HEALTHY

The repository passes the full scientific-integrity gate (`cm validate
--with-tests`, 8/8 checks), the lint/type ratchet is at baseline (no new debt),
the frozen artifacts are SHA-verified, and the layered architecture is
machine-enforced. No P0/P1 scientific-integrity issue is open (see
[critical code review](critical_code_review.md)).

## Quality scorecard

| Dimension | Metric | Value | Status |
|-----------|--------|-------|--------|
| **Tests** | test functions / files | 186 / 21 | PASS (all green) |
| **Lint ratchet** | ruff / mypy vs baseline | 32/32 · 93/93 | PASS (no new debt) |
| **Invariants** | frozen-property guards | 10 | PASS |
| **Frozen artifacts** | registered / frozen / SHA-verified | 12 / 12 / 12 | PASS |
| **Claims** | registered (levels) | 19 (L0×7, L3×8, L5×3, L6×1) | PASS (graph valid) |
| **Experiments** | registered | 8 | PASS |
| **Security** | secret scan + audit + human-data guard | clean | PASS |
| **Leakage** | scanner (L1-L5) | PASS | PASS |
| **Architecture** | import-boundary (layered) | enforced, 3/3 | PASS |
| **Reproducibility** | disaster recovery (clean-room) | reproduced | PASS |
| **Human data** | staged pre-gate | none | PASS |

## Size & structure

| Area | Value |
|------|-------|
| Git-tracked files | 629 |
| Library (`src/causal_mind`) | 7,736 LOC · 20 subpackages + 9 top modules |
| Experiment scripts (`data/scripts`) | 13,125 LOC |
| Tests | 2,464 LOC |
| Markdown (docs + reports) | 1,768 files (53 under `reports/`) |

## Validation evidence

```
$ cm validate --with-tests
[PASS] lint/type ratchet
[PASS] invariants
[PASS] claims graph
[PASS] registry integrity
[PASS] claim linter
[PASS] security audit
[PASS] human-data guard
[PASS] tests (pytest full)
VALIDATE: PASS (8 checks green)
```

## Known issues (tracked, not blocking)

From the [critical code review](critical_code_review.md):

- **F2 (P1, portability):** ~90 `data/scripts/*.py` hard-code the pod path.
  Library + CLI + tests are portable; the one-off scripts are not yet.
  Migration to `causal_mind.paths` is a safe follow-up.
- **F3-F7 (P2/P3):** manual leakage-script list, L5 trust-me check, a `None`
  placeholder field, lineage SHAs not re-verified, two RNG libraries. None
  affect the validity of a frozen result.

## Health trends

- **Improving:** professionalization added the research CLI, governance docs,
  runbooks, import-boundary enforcement, human-data guard, and centralized
  constants/paths/errors — all of which reduce future drift and onboarding cost.
- **Stable:** the frozen scientific core (CM-2…CM-9A, CM-8) is unchanged and
  re-verified (invariants + SHA registry + no-drift).
- **Watch:** script portability (F2) and the manual leakage-script list (F3) are
  the two items most likely to bite a new contributor or a new deep-dive script.

## Verdict

The repository is in a **professional, maintainer-ready** state: it validates
cleanly, its scientific record is frozen and integrity-checked, its architecture
is explicit and enforced, and its governance is documented. It is fit for expert
maintenance and for the pre-human freeze it supports.
