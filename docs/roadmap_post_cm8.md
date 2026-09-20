# CAUSAL MIND — Roadmap After CM-8

What happens next, in order, with the gates and dependencies. Part of the
`cm8-prehuman-v1.0` freeze. The immediate future is gated on three external approvals.

## Phase 0 — Now (pre-human, done)

- The program is at `CM8R_PREHUMAN_HARDENED` (10/10 gates). The pre-human freeze
  `cm8-prehuman-v1.0` is tagged and hash-verified. **No human data collected.**

## Phase 1 — External approvals (the only blockers)

1. **Supervisor sign-off** on the frozen protocol + pre-human freeze.
2. **Ethics approval** (University of Vienna Ethics Committee). Package ready in
   `docs/ethics/`; submission deadline **5 Oct 2026** for the **5 Nov 2026** meeting.
3. **Pilot authorization** (CM-8P).

*These are external; there is no hidden technical blocker.*

## Phase 2 — Pilot (CM-8P, gated)

- A small, gated run (3–5 participants).
- **Purpose:** operational GO/ITERATE/STOP only — **not** an analysis of the ATE.
- Checks: capture modality, latency in the wild, participant burden (~28 min / 96 thoughts),
  manipulation check, report-reactivity, engine stability.
- **Gate:** GO → confirmatory; ITERATE → fix operational issues (no protocol change);
  STOP → stop (a valid outcome).

## Phase 3 — Confirmatory run (CM-8H, gated)

- The frozen CM-8 experiment: within-subject, randomized, 4 conditions, N=20, 24 trials.
- Primary: ATE_GENERAL and ATE_CUE vs pooled CONTROL/SHAM, subject-clustered permutation,
  B=10,000, two-sided α=0.05.
- **A positive or a null is a result.** The protocol is not changed to chase a positive.
- **Output:** the first causal test of voluntary redirection of a predicted thought.

## Phase 4 — Interpretation and publication

- **If the confirmatory run is positive:** a causal result for the redirection of a
  predicted thought (L6/L7, subject to the reviewer gate). Paper 2/3 become the causal
  papers.
- **If the confirmatory run is null:** a valid null, reported as a result. The thesis floor
  is Option B (forecast → explain → intervene method), which is already complete.
- **Publication:** Paper 1 (prediction) is ready to submit; Paper 2 (causal method) is ready
  to submit; Paper 3 (protocol + result) completes after the run.

## Phase 5 — Theoretical extension (CM-9, optional / parallel)

- Develop the synthetic Oracle lab (CM-9A) into a theory of prediction vs. intervention
  (RPR/PIE; computational irreducibility; game-theoretic best response).
- Use the theory to (a) choose detectable interventions and (b) interpret the BRP.
- This is a separate research direction; it does not depend on the human run.

## Phase 6 — Scaling and generalization (long-term)

- Cross-corpus / cross-task generalization of the prediction (the single-corpus limitation).
- Larger-N confirmatory runs if the effect is small (the power surface guides N).
- The category (non-semantic) arm.
- New intervention modalities (if the pilot suggests them).

## What is explicitly NOT on the roadmap

- Reopening a closed negative result to obtain a positive.
- Changing the frozen CM-8 confirmatory protocol (Workstream A).
- Optimizing the design based on simulation to chase a positive.
- Any free-will claim.

## Dependency summary

```
Phase 0 (done)
   └─> Phase 1 (sign-off + ethics + pilot auth)   [external]
          └─> Phase 2 (pilot CM-8P)                [gated]
                 └─> Phase 3 (confirmatory CM-8H)  [gated]
                        └─> Phase 4 (interpret + publish)
Phase 5 (CM-9 theory) — parallel, independent of the human run
Phase 6 (scaling) — long-term, after Phase 4
```
