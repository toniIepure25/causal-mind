# CM-LAB Pull-Request Checklist (CM-LAB §50)

Every PR to `causal-mind-v2` must satisfy the gates below before merge. The orchestrator merges
only validated work; the reviewer has BLOCK authority.

## 1. Scientific discipline (hard gates)

- [ ] No change to the frozen `cm8-prehuman-v1.0` release or the frozen CM-8 confirmatory
      protocol (v1.0). Verify: `python data/scripts/cm_lab_registry.py --check`.
- [ ] No change to C-001..C-012 claim levels without an explicit revision (OLD/NEW/REASON/
      EVIDENCE/COMMIT) in `docs/claims_registry.md`.
- [ ] Any NEW scientific claim is registered in `claims/claims.json` with dataset/protocol/
      script/report/statistic/commit/reproduction/red-team. Verify:
      `python data/scripts/cm_lab_claims_graph.py --check`.
- [ ] Subject-disjoint splits only (no random row splits on temporal data). Verify:
      `python data/scripts/cm_leakage_scan.py` (L1).
- [ ] Strictly prospective targets (no target in the history window). Verify:
      `python data/scripts/cm_leakage_scan.py` (L2, L4).
- [ ] The reviewer's leakage audit passes before any result is reported as validated.

## 2. Reproducibility (hard gates)

- [ ] Every result has a runnable reproduction command (`.venv/bin/python data/scripts/<x>.py`).
- [ ] Every result is machine-readable (a JSON report under `reports/`).
- [ ] All fitting/tuning on TRAIN only; no test-set tuning. Verify:
      `python data/scripts/cm_leakage_scan.py` (L3).
- [ ] Seeds are fixed and recorded in the report JSON.
- [ ] `bash scripts/validate_project.sh` passes (lint ratchet + tests + invariants + registries
      + claim linter + secret scan).

## 3. Security & hygiene (hard gates)

- [ ] No secrets, tokens, SSH keys, or credential files added. Verify:
      `python data/scripts/cm_lab_security.py --check`.
- [ ] No public (0.0.0.0) binds; local tooling binds 127.0.0.1 only.
- [ ] No outbound telemetry / external LLM calls.
- [ ] Caches/scratch under the project PVC (`/home/jovyan/work`), not the system temp.

## 4. Negative results & honesty (soft gate)

- [ ] A negative result is reported as a result (not bent to save a hypothesis).
- [ ] Claim levels are not inflated (L0-L8 scale; see `docs/claims_registry.md`).
- [ ] The red-team field of each claim states the strongest attack and why it was addressed.

## 5. Human-data boundary (hard gate)

- [ ] No real human data collected pre-ethics (synthetic pseudonyms only). Verify:
      `tests/test_invariants.py` (CM-8 no-real-human-data invariant).
- [ ] Any human-facing work is gated on ethics approval (deadline 5 Oct 2026) and the CM-8P
      pilot authorization.

## Merge rule

The orchestrator merges only when **all hard gates pass** and the reviewer has not BLOCKed.
No git push from agents (orchestrator/human pushes); no force-push.
