# CM-LAB Scorecard (S86)

**Overall: `CMLAB_PROFESSIONAL_RESEARCH_PLATFORM_READY`**

Consolidated status of the CM-LAB target states. Each is backed by a runnable check.

| target state | status | evidence / how to verify |
| --- | --- | --- |
| **CMLAB_RESEARCH_OS_PASS** | PASS | Env reproducible (S4), one-command validation (S6), invariants (S7), claim graph (S8), registries (S9-11), CI (S12). Verify: `bash scripts/validate_project.sh` |
| **CMLAB_DISASTER_RECOVERY_PASS** | PASS | Fresh clone -> bootstrap -> validate -> integrity, all green. Verify: `bash scripts/disaster_recovery.sh` |
| **CMLAB_CLAIM_TRACEABILITY_PASS** | PASS | Every claim (C-001..C-012, C-101) links to dataset/protocol/script/report/statistic/commit/reproduction/red-team. Verify: `python data/scripts/cm_lab_claims_graph.py --check` |
| **CMLAB_SECURITY_PASS** | PASS | 0 secrets, 0 tracked credential files, 0 public (0.0.0.0) binds, 0 outbound telemetry, 90 pinned deps. Verify: `python data/scripts/cm_lab_security.py --check` |
| **External validation decision** | `CMXVAL_PARTIAL` | CM-XVAL-1 on Open Play (openESM 0075): model beats strongest frozen baseline at all horizons (gain +0.016..+0.034, CIs exclude 0); target-shuffle perm p=0.71. New claim C-101. |

## Scientific invariants held (S7, `tests/test_invariants.py`)
- CM-2 subject-disjoint split (83/18/17, no overlap).
- CM-3 strictly prospective targets (all horizons > 0).
- CM-5 HRF-safe buffer (6 s) + window (15 s).
- CM-6 unidentified counterfactuals are refused (engine raises).
- CM-7 randomization-aware inference preserved.
- CM-8 confirmatory alpha = 0.05, basin tail = 0.10, BRP definition + code SHA unchanged.
- CM-8 no real human-data collection pre-ethics (synthetic pseudonyms only).
- CM-9A synthetic results isolated from empirical claims.

## Frozen record integrity (S10)
12 frozen artifacts SHA-verified unchanged (`cm_lab_registry.py --check`). The
`cm8-prehuman-v1.0` release and the frozen CM-8 confirmatory protocol v1.0 are untouched.

## What changed in CM-LAB (post-freeze, all additive)
- Research-OS infrastructure (env, validation, invariants, claim graph, registries, CI,
  disaster-recovery, security).
- One external-validation result (C-101, `CMXVAL_PARTIAL`) — a NEW claim, per protocol.
- No change to C-001..C-012, the frozen protocol, or the frozen release.
- No human data collected.

## Known limitations / not done this phase
- External validation on a single dataset (Open Play); a second domain (e.g., van Halem
  "Daily event", openESM 0070) would strengthen the `CMXVAL_PARTIAL` conclusion.
- Dependency vulnerability-DB audit (needs a reachable vuln feed); pinned `uv.lock` is the control.
- The scientific deep-dive workstreams (uncertainty quantification, dynamics, Oracle theory)
  are queued but not the gate for platform readiness.
