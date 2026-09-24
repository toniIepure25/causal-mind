# CM-LAB Research Standards & Tooling (CM-LAB §50-59)

**Decision:** `CMSTD_IN_PLACE`
**Machine-readable:** `reports/cm_leakage_scan/cm_leakage_scan.json` (leakage), `reports/registry_report.md` (registries), `reports/security_audit.json` (security)

This report maps each §50-59 standard to the runnable tool that enforces it. Most of the
platform was built in the prior CM-LAB phase; this deep dive adds the dedicated **data-leakage
scanner** (§55) and consolidates the mapping. Every standard has a one-command verification.

---

| § | Standard | Enforcing tool | Status | Verify |
|---|---|---|---|---|
| 50 | PR checklist | `docs/protocol/pr_checklist.md` | IN PLACE | human + reviewer gate |
| 51 | Config immutability | `cm8r_freeze_forecaster.py`, `cm8_sw_freeze.json`, `cm_lab_registry.py --check` (12 frozen SHAs), `tests/test_invariants.py` | IN PLACE | `python data/scripts/cm_lab_registry.py --check` |
| 52 | Randomness audit | `cm8r_randomization.py`, `cm8_randomization_manifest.json` (seed, permutations, basin draws) | IN PLACE | `python data/scripts/cm8r_randomization.py` |
| 53 | Dataset locking | `cm2_split_seal.json`, `cm3_protocol_seal.json`, `integrity_osf.py`, `validate_osf.py`, registry lineage | IN PLACE | `python data/scripts/validate_osf.py` |
| 54 | Data schemas | `data/derived/thought_events/*_thoughts.tsv` schema (subject, index, timestamp, text, embedding-dim); `state_v1.ThoughtState` | IN PLACE | `python data/scripts/audit_ds006067.py` |
| 55 | **Leakage scanner** | **`cm_leakage_scan.py`** (NEW): L1 subject-disjoint, L2 prospective targets, L3 fit-on-test, L4 target-in-history, L5 per-entry embeddings | **NEW / PASS** | `python data/scripts/cm_leakage_scan.py` |
| 56 | Pre-flight | `cm8r_readiness.py`, `cm8_dry_run.py`, `scripts/validate_project.sh` | IN PLACE | `bash scripts/validate_project.sh --fast` |
| 57 | Compute accounting | per-script `runtime_s` in every report JSON; `verify_gpu.py` (A100-SXM4-40GB); wall-clock logged in research_log | IN PLACE (lightweight) | inspect report JSONs |
| 58 | Portability | `bootstrap_environment.sh`, `verify_env.py`, pinned `uv.lock` (90 deps), `HF_HOME` on PVC | IN PLACE | `bash scripts/bootstrap_environment.sh` |
| 59 | Benchmark | `verify_gpu.py` (GPU), `cm8r_latency.py` (realtime engine latency), per-script `runtime_s` | IN PLACE | `python scripts/verify_gpu.py` |

## §55 Leakage scanner (new this deep dive)

`data/scripts/cm_leakage_scan.py` is the reviewer's first-line leakage audit for the scientific
deep-dive scripts. It re-verifies the frozen invariants and statically audits each deep-dive
script:

- **L1 subject-disjoint** (CM-2 seal): no subject in >1 split. PASS (83/18/17, no overlap).
- **L2 prospective targets** (CM-3 seal): all event horizons > 0. PASS ([1,2,3,4,5,6,8,10]).
- **L3 fit-on-test**: no predictive `.fit()` is fed a test-named variable. PASS (all fits on
  `tr_*`/`train_*` or per-subject descriptive NearestNeighbors).
- **L4 target-in-history**: no `target_index` inside a model-input `concat([...])`/`history=[...]`.
  PASS (the model input is always `sample.history`; `st[s.target_index].embedding` is used only
  as ground truth for comparison).
- **L5 per-entry embeddings**: MiniLM embeddings are computed per-entry (no context window
  spanning the target). PASS.

**Decision: `CMLEAK_PASS`.**

## What is NOT covered (honest gaps)

- **§57 compute accounting** is lightweight (per-script `runtime_s` + GPU verify), not a full
  cost ledger. Adequate for this phase; a formal ledger is a future direction.
- **§59 benchmark** covers GPU presence, realtime-engine latency, and per-script runtime, not a
  standardized MLPerf-style benchmark. Adequate for this phase.
- **Dependency vulnerability-DB audit** needs a reachable vuln feed; the pinned `uv.lock` is the
  control (noted in the prior scorecard).

## Guardrails

- All tools are read-only audits (no mutation of frozen artifacts).
- The leakage scanner is static + invariant-based; the reviewer should also manually review any
  new script before it is reported as validated.
- No CM-8 change. No human data.
