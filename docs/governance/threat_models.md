# Threat Models

**Status:** canonical · **Companions:** [SECURITY.md](../../SECURITY.md),
[data classification](data_classification.md)

Three threat models, each with assets, threats, and the controls that mitigate
them. Controls are enforced in code (pre-commit, CI, `cm validate`) wherever
possible so they cannot be silently skipped.

## 1. Security threat model

**Assets:** the repository, frozen artifacts, the Qwen endpoint, the pod, any
future participant data.

| Threat | Likelihood | Impact | Control |
|--------|-----------|--------|---------|
| Secret committed to Git | medium | high | `cm security scan` + CI secret scan (hard-fail); pre-commit lint gate; `.env.example` placeholders only. |
| Public network bind | low | high | `data/scripts/cm_lab_security.py --check` forbids non-loopback binds; agents bind to `127.0.0.1`. |
| Telemetry / data exfiltration | low | high | Security audit forbids telemetry endpoints; CM-8 inference is offline. |
| Credential file in repo | low | high | Security audit forbids credential files; `.gitignore` excludes them. |
| Supply-chain (deps) | low | medium | `uv.lock` pins versions; `uv sync` is reproducible; new deps require review. |
| Malicious agent action | low | medium | Sandboxed agent tools (`agent/tools.py` path checks); reviewer BLOCK authority; no agent git push. |

**Residual risk:** the Qwen endpoint and pod are trusted infrastructure; a
compromised pod is out of scope for repo-level controls (platform responsibility).

## 2. Scientific-integrity threat model

**Assets:** the validity of every reported result; the frozen protocols; the
claim registry.

| Threat | Likelihood | Impact | Control |
|--------|-----------|--------|---------|
| Test-set leakage | medium | critical | Subject-disjoint splits (sealed); `cm_leakage_scan.py` (CI); reviewer leakage audit required before a result is "validated". |
| Protocol drift | medium | critical | Frozen protocol seals (`cm2_split_seal.json`, `cm3_protocol_seal.json`); `cm8_no_drift.py` (`cm reproduce cm8`); invariants tests. |
| Frozen artifact tampering | low | critical | SHA-256 registry; `cm artifacts verify` (CI); immutable freeze tags. |
| Overclaiming | medium | high | Claim levels 0-8; `cm_pub_claim_linter.py` (forbids overclaiming language); reviewer audit. |
| Result shopping / p-hacking | medium | high | Frozen primary protocol before touching test outcomes; negative controls; "a negative result is a result" (AGENTS). |
| Random row split on temporal data | medium | critical | Validation policy #1 (subject-disjoint only); invariants tests. |
| Nondeterminism masquerading as reproducibility | low | medium | Seeded RNGs; run IDs; clean-room disaster recovery (`disaster_recovery.sh`). |

**Residual risk:** no control can prove the absence of all leakage; the defense
in depth (seals + scanner + reviewer + invariants) makes a leak require
simultaneously defeating several independent gates.

## 3. Data-protection threat model

**Assets:** participant privacy (when human data exists post-gate); GDPR
compliance.

| Threat | Likelihood | Impact | Control |
|--------|-----------|--------|---------|
| Real human data committed pre-gate | medium | critical | `human_data_guard.py` (pre-commit + CI hard-fail); data classification C4. |
| Raw thought text leaves the machine | low | critical | Privacy-by-design: embeddings only, no raw text egress; CM-8 offline. |
| Re-identification | low | high | Pseudonymization; no direct identifiers in C1/C2/C3; `privacy/pii.py`. |
| Data leaked via a report | low | high | C3 must not embed C4; leakage scanner; reviewer audit. |
| Unauthorized access to PVC | low | high | Platform access control; no public service exposure (bind 127.0.0.1). |

**Residual risk:** before the human gate there is **no** human data in the repo,
so the primary exposure is the *introduction* of C4 data, which the guard
blocks at commit time and in CI.

## How the models are kept current

- Every new experiment/data source: update the relevant table in
  [new_experiment runbook](../runbooks/new_experiment.md).
- Every security-related change: re-run `cm security scan` and review the
  affected row.
- The reviewer red-teams against these models before a result is validated.
