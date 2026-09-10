# Smoke: Orchestrator Next-Task Proposal

Task SMOKE-ORCHESTRATOR-001. First three real tasks to queue after smoke tests pass,
ordered by dependency. All respect the frozen validation protocol (subject-disjoint
splits, no holdout peeking, reviewer leakage audit before any result is reported) and
the "audit before download" policy (no bytes downloaded before the metadata audit
passes; every file checksummed into `data/manifests/ds006067.yaml`).

## 1. CM1-001 — ds006067 authoritative metadata audit
- **Milestone:** CM1_DATA_AUDIT
- **Objective:** Verify ds006067 metadata (subjects, runs, TR, transcript/timestamp
  format, thought boundaries, annotations, license, footprint) from openneuro.org
  sources only — no download — and write `data/manifests/ds006067.yaml` with
  checksums, flipping audit status to `verified`.
- **Owner:** data

## 2. CM2-001 — Thought-event extraction + frozen split definitions
- **Milestone:** CM2_THOUGHT_STATE_V0
- **Objective:** After the audit passes, download the minimal subset (1–2 subjects,
  1 run each), build thought events per the frozen definition, and freeze
  subject-disjoint train/val/test split definitions (seeds recorded,
  `validate_split_integrity` passing) — final holdout untouched.
- **Owner:** data

## 3. CM3-001 — Baseline battery B0–B2 on frozen splits
- **Milestone:** CM3_NEXT_BASELINES
- **Objective:** Run the next-thought baseline battery (B0 marginal, B1 previous,
  B2 Markov) on the frozen splits with subject-level permutation controls and
  negative controls; register results at L2/L3 only if the reviewer's leakage
  audit passes (feeds GATE B).
- **Owner:** forecasting
