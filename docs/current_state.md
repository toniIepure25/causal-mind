# Current State

## Project state

`CM2_UNBLOCKED_OSF_BEHAVIORAL_SOURCE`
(CM-1 = `CM1_PASS`; CM-2 = `CM2_PASS`. OpenNeuro S3 outage is no longer a CM-2
blocker — behavioral data is sourced from OSF `a56rm`. OpenNeuro is still
required for CM-5 neural analyses; the S3 retry is kept alive.)

## Current stage

Phase 2: CM-1 (data) and CM-2 (non-neural thought-state + next-thought
prediction) complete and pushed. Next: CM-2 iteration (optional) and CM-5
(neural), which needs OpenNeuro.

## Validated results

- L0: Qwen endpoint `Qwen/Qwen3.8-27B-FP8` reachable at `http://127.0.0.1:18000/v1`
  (chat + tool calls); tunnel supervisor self-heals (direct port-forward, no Caddy).
- L0: task queue claim locking, worktree isolation, agent harness; all six agents
  smoke-tested (SMOKE-*-001).
- **CM-1 (L0 data integrity):** ds006067 audited across its two authoritative
  sources — OpenNeuro `ds006067 v2.0.0` (MRI) + OSF `a56rm` (behavioral). 118
  subjects; sentence-level transcripts (118), word-level (102), GPT ratings (118),
  human-validated ratings (18). Cohort integrity: 10/10 checks pass. Red-team GO.
- **CM-2 (L3):** past thought history (a k≈3 window of frozen MiniLM text
  embeddings) predicts next-thought semantics **above all baselines B0-B7**
  (0.3623 [0.3523, 0.3720] vs strongest 0.3265 [0.3149, 0.3381], non-overlapping
  CIs), out-of-sample, subject-disjoint (83/18/17, sealed), prospective;
  permutation null p=0.0000; reproduced from a clean process. Effect is modest;
  category arm unvalidated; no causal claim. Red-team GO.

## Failed hypotheses

(none yet — CM-2 is a modest positive, not a null)

## Active tasks

- CM-2 iteration (optional, `CM2_ITERATE`): categorical head; GPT-rating features
  beyond text; small GRU for non-linear headroom.
- CM-5 (neural): requires OpenNeuro BOLD (S3 retry kept alive).

## Blockers

- **OpenNeuro S3 outage** (was blocking CM-2; now only blocks CM-5). Background
  retry kept alive. Not a CM-2 blocker.
- **Token lifecycle:** Run:ai CLI tokens expire ~daily; a human must complete
  `runai login remote-browser` on expiry. Runbook: `docs/runbooks/qwen_tunnel.md`.

## Next gates

- GATE (CM-2 iteration): categorical arm + GPT-rating ablation.
- GATE (CM-5): neural signal, once OpenNeuro BOLD is reachable.

## Key commit hashes

- `176670e` CM-1 complete (data audit, loader, red-team GO)
- `7004d66` CM-2 OSF pivot (dual-source, OSF loader, ontology, integrity, amendment)
- (CM-2 results + red-team + final report commit follows)

## Exact reproducibility commands

```bash
# on the pod, via SSH as jovyan (sidecar netns)
cd /home/jovyan/work/causal-mind-v2
scripts/qwen_tunnel_supervisor.sh status
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests data/scripts
# CM-2 decisive run (deterministic, ~6 min):
HF_HOME=/home/jovyan/work/.hf-home TRANSFORMERS_CACHE=/home/jovyan/work/.hf-home \
  PYTHONPATH=src .venv/bin/python data/scripts/run_full_evaluation.py
```

## Environment notes

- Working root: `/home/jovyan/work/causal-mind-v2` (jovyan-owned).
- Behavioral data: `data/raw/osf/...` (immutable) → `data/derived/thought_events/...`.
- All git commands need `safe.directory=*` (NFS maps ownership to uid 65534).
- The SSH session runs in a sidecar network namespace; the tunnel supervisor binds
  the port-forward inside the SSH netns.
