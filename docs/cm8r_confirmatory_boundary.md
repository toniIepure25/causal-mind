# CM-8R / CM-9A — Confirmatory Boundary (workstream separation)

This document is the contract that keeps the **frozen CM-8 confirmatory experiment**
intact while we exhaust all useful pre-human work. It is normative: every CM-8R and
CM-9A deliverable must respect it.

## The two workstreams

### Workstream A — `CM-8 CONFIRMATORY` (FROZEN)
- The human experiment defined by `docs/ethics/cm8_research_plan.md` (protocol v1.0) and
  `docs/ethics/cm8_preregistration_final.md` (preregistration v1.0, sealed).
- **Frozen and NOT to be changed** by any simulation, replay, or engineering result:
  - primary endpoint: BRP at the frozen horizon `h*` (target 2);
  - treatment definitions: CONTROL / SHAM / GENERAL REDIRECT / SPECIFIC CUE;
  - basin rule: 90th-percentile held-out forecast-error radius (basin tail = 0.10);
  - confirmatory test level: two-sided α = 0.05, subject-clustered permutation, B = 10,000;
  - randomization design: within-subject, counterbalanced, seed + manifest;
  - primary estimands: `ATE_GENERAL`, `ATE_CUE` vs pooled CONTROL/SHAM (SHAM-alone
    sensitivity); BH-FDR q = 0.05 over the primary family;
  - sample size: N = 20, 24 trials/subject (recruit 25);
  - exclusions: pre-specified, outcome-independent, intent-to-treat, ≥ 16/24 valid.
- **No human data is collected** until ethics approval + the pilot. CM-8P is not begun.

### Workstream B — `CM-8R / CM-9A EXPLORATORY PRE-HUMAN`
- Simulation, replay, engineering, robustness, and theory. **No human data.**
  - CM-8R: ghost pilot, synthetic participant world, Monte Carlo, power surface, BRP
    adversarial red team, basin robustness, realtime engine, latency, offline mode,
    failure injection, transactional logging, randomization red team, privacy hardening,
    clean-room reproduction, blinding, burden simulation.
  - CM-9A: the synthetic Oracle lab (prediction-reveal / veto / redirect agents, recursive
    predictor, RPR, entropy, games, computational irreducibility).

## What B may and may not do

**B may inform:**
- future **protocol amendments** (a formal, signed, dated amendment that supersedes a
  specific frozen clause — never a silent edit);
- **secondary / exploratory analyses** (pre-declared as such; they cannot rescue a null
  primary);
- **future studies** (CM-8P pilot design, CM-9 Oracle design, new experiments);
- the **operational** pilot (breaks, session length, operator alerts, QC thresholds) —
  these are feasibility parameters, not scientific estimands.

**B may NOT:**
- rewrite Workstream A's primary endpoint, treatment definitions, basin rule, α,
  randomization design, or primary estimands;
- select a "better" basin percentile, horizon, or reference arm because a simulation
  shows more power;
- change the frozen N solely to improve simulated power (only a formal amendment,
  justified on feasibility/ethics grounds, may do so);
- use a simulated positive effect as evidence the real experiment will succeed;
- call a null result a failure, or a simulation a validation of the causal hypothesis.

## Change control

Any change to a frozen clause requires, in order:
1. a written **protocol amendment** in `docs/ethics/` (numbered, dated, signed by the
   responsible study-law body / supervisor);
2. an update to the preregistration with a new seal hash;
3. an entry in `docs/research_log.md` and `docs/claims_registry.md`;
4. a note in this file recording the amendment.

Until such an amendment exists, Workstream A is immutable.

## Provenance of the frozen record (verified 2026-09-17)

- GitHub `main` = `feb3257` (CM-8E ethics freeze) and its descendants.
- Preregistration v1.0: basin tail = 0.10, confirmatory α = 0.05 (two-sided).
- Monte Carlo calibration: type-I at α = 0.05 = 0.047 (MC 95% CI [0.013, 0.080]);
  BRP_control = 0.0989 ≈ 0.10; recovery bias < 0.003.
- Independent REVIEWER clean-process reproduction: CALIBRATION PASS (alt-seed 0.040).
- CM-8R additions (this workstream) are recorded as new commits on top of `feb3257`;
  they do not rewrite any historical result or claims-registry entry.
