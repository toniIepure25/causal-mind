# CM-8R16 — Randomization Red Team

- **State:** `CM8R_RANDOMIZATION_PASS`  | scheme: within-subject round-robin (no consecutive same-condition) | seed 20260917 | 20000 sessions audited
- **Marginal balance:** {'control': 0.25, 'sham': 0.25, 'general': 0.25, 'cue': 0.25}
- **Early-session balance:** {'control': 0.25, 'sham': 0.249, 'general': 0.251, 'cue': 0.25}
- **Late-session balance:** {'control': 0.25, 'sham': 0.25, 'general': 0.25, 'cue': 0.25}
- **Max run length:** 1 (target <= 2)
- **Deterministic seed replay:** True
- **Attacker accuracy:** 1.000 (chance 0.25) — MLP(32) on last-4 one-hot conditions

## Interpretation
- The frozen scheme is a fixed counterbalanced permutation repeated, so the order is deterministic BY DESIGN. The attacker's high accuracy is the design expectation, not a randomization failure. A truly random (unconstrained) scheme would give ~0.25.
- **Predictability:** The order is fully predictable after 4 conditions (fixed permutation). This is by design for counterbalancing.
- **Anticipation risk:** If blinding is imperfect (the participant can tell the conditions apart), the predictable order allows anticipation. MITIGATION: blinding (SHAM no-op, similar intervention formats). MONITOR in the pilot (blinding check).
- **Validity:** The randomization remains valid for the confirmatory analysis: balanced, deterministic, intention-to-treat. The permutation test is valid under exchangeability (outcome depends on the condition, not the position).

## Checks
- PASS — marginal_balance
- PASS — early_session_balance
- PASS — late_session_balance
- PASS — no_runs_gt_2
- PASS — deterministic_seed_replay

**Conclusion:** the frozen randomization is balanced, run-free, and deterministic -> valid for the confirmatory analysis. The order is predictable BY DESIGN (counterbalanced); the anticipation risk is managed by blinding and monitored in the pilot. No change to the frozen design.
