# CAUSAL MIND — Evidence Matrix

Claim-level traceability. Every claim in the program is mapped to its **level** (0–8,
see `docs/claims_registry.md`), its **exact evidence value** (copied verbatim from the
committed report), the **report**, the **code**, and the **reproduction command**.
No claim is worded above its level. This matrix is part of the `cm8-prehuman-v1.0` freeze
and contains no human data.

## Level scale

- **L0** pipeline sanity (code runs, formats parse, round-trips verified)
- **L1** association (variables co-vary; no causal language)
- **L2** out-of-sample prediction (subject-disjoint, above chance)
- **L3** incremental prediction beyond strong baselines (B0–B5)
- **L4** cross-subject generalization (repeated subject-level splits)
- **L5** temporal prospective prediction (future horizon, lag-audited)
- **L6** causal evidence from valid intervention / identification
- **L7** closed-loop trajectory redirection
- **L8** recursive prediction of attempted escape

## Claim → evidence table

| id | claim (short) | level | exact evidence value | status | report |
| --- | --- | --- | --- | --- | --- |
| C-001 | Qwen endpoint + agent harness operate on the pod | L0 | smoke tests 2026-09-09 | validated | `reports/agents/` |
| C-002 | ds006067 dual-source dataset integrity (118 subjects; 10/10 cohort checks) | L0 | 118 subjects; 10/10 integrity checks | validated | `reports/cm2_results.json` (seal `67505261…`) |
| C-003 | Past thought history predicts next-thought semantics above baselines | L3 | held-out 0.3623 [0.3523, 0.3720] vs B0 0.3167 [0.3078, 0.3250]; perm p=0.0000 | validated | `reports/cm2_results.json` |
| C-004 | Cognitive history predicts future thought semantics at every horizon h=1..10 | L5 | PredictiveGain +0.0349 [0.0253, 0.0445] (h=1) → +0.0044 (h=10), all CIs excl. 0; perm p=0.0000 | validated | `reports/cm3_results.json` |
| C-005 | HRF-safe BOLD has NO incremental value for thought content | L5 | N2/Schaefer-400 gain −0.088/−0.085/−0.085/−0.090 (h=1/3/5/10), 0/16 subjects positive, perm p=1.0 | validated (negative) | `reports/cm5_decisive_results.json` |
| C-006 | CM-6A observational candidate SCM; 0 edges causally identifiable | L5 | 124 candidate edges, 0 identifiable; 39/272 CI edges survive BH-FDR; 0/126 mediator triples | validated (negative ID) | `reports/cm6_observational_results.json` |
| C-007 | CM-6B public-intervention dataset audit | L0 | 16 candidates, 9 verified; only ds005494 has do(X)+measured future state; none test voluntary redirection (E8) | validated (audit) | `reports/cm6_candidate_scm.json` |
| C-008 | CM-6D/E causal machinery (CTE, BRP, basin, counterfactual engine) | L0 | 61/61 tests pass; ruff clean; engine refuses to label unidentified counterfactuals causal | validated (machinery) | `tests/` |
| C-009 | CM-6 decision: observational only; Oracle gated (6 unmet criteria) | L0 | 0/84 edges identifiable (analysis_7); CM-6H/CM-6I designed, not executed | design-only | `reports/cm6_observational_results.json` |
| C-010 | CM-7 public-intervention method validation (ds005494) | L6 | ATE −0.0386, 2-phase perm p=0.0733, list CI [−0.079, 0.002]; integrity 3328/3330 (99.94%); leakage PASS | validated (method; null effect) | `reports/cm7_results.json` |
| C-011 | CM-8R pre-human hardening (no human data) | L0 | clean-room bit-identical; BRP_control 0.0785 ≈ 0.10; chaos 7/7; privacy 12/12; 10/10 gates | validated (pre-human) | `reports/cm8r_readiness/cm8r_readiness.json` |
| C-012 | CM-9A synthetic Oracle lab (no human data) | L0 | 4 conditions × 11 policies; HIDDEN+O5 RPR=1.48 (least predictable); VETO+O0 RPR=0.16 (most) | design-only (synthetic) | `reports/cm9a_oracle_lab/cm9a_oracle_lab.json` |

## Per-claim detail

### C-003 — CM-2 next-thought prediction (L3)
- **Value:** main model (linear_transition, k=3, α=100) held-out semantic cosine
  **0.3623 [0.3523, 0.3720]**; strongest baseline B0_marginal **0.3167 [0.3078, 0.3250]**;
  all 8 baselines beaten; permutation p = 0.0000.
- **Data:** 118 subjects, 6,436 thoughts; subject-disjoint 83/18/17 (seal `67505261…`).
- **Report:** `reports/cm2_results.json`
- **Code:** `src/causal_mind/thought/encode.py`, `src/causal_mind/thought/state_v1.py`,
  `src/causal_mind/forecast/multihorizon_model.py`
- **Reproduce:** `.venv/bin/python data/scripts/run_cm2.py` (see `docs/releases/cm8_prehuman_v1.md`)

### C-004 — CM-3 multi-horizon forecasting (L5)
- **Value:** model beats the strongest horizon-specific baseline at every h∈{1,2,3,4,5,6,8,10}.
  Gain over strongest baseline: h=1 +0.0349 [0.0253, 0.0445]; h=2 +0.0261 [0.0205, 0.0321];
  h=3 +0.0152 [0.0091, 0.0220]; h=4 +0.0114 [0.0070, 0.0165]; h=5 +0.0093 [0.0038, 0.0148].
  Smooth monotonic decay; survives time-shuffled / transition-destroyed / random-target nulls (p=0.0000).
- **Report:** `reports/cm3_results.json`
- **Reproduce:** `.venv/bin/python data/scripts/run_cm3.py`

### C-005 — CM-5 neural incremental value (L5, negative)
- **Value:** primary N2/Schaefer-400 IncrementalNeuralGain (M4−M2) = **−0.088 / −0.085 /
  −0.085 / −0.090** at h=1/3/5/10, 95% CIs excluding 0, **0/16** test subjects positive,
  permutation p = 1.0, Cohen's d = −2.51. Capacity ladder non-positive (N1 ~−0.001,
  N3 ~−0.016). NC4 (nuisance-only) → 0. Replicated by NC1/NC2/NC3/NC5/NC6 controls.
- **Data:** 106 eligible subjects (73/17/16 after F2 tSNR + alignment gates); onset_min_s=36.
- **Report:** `reports/cm5_decisive_results.json`
- **Reproduce:** `.venv/bin/python data/scripts/run_cm5.py`

### C-006 — CM-6A observational candidate SCM (L5, negative identification)
- **Value:** 124 candidate edges, **0 causally identifiable** (all blocked by unmeasured
  confounding, incl. the per-subject GPT-rating baseline). 39/272 CI edges survive BH-FDR;
  0/126 mediator triples survive. Robust signal: linguistic-load cluster (duration→gap
  r_partial = 0.828).
- **Data:** 118 subjects, 6,436 thoughts; α=0.05, max_lag=3.
- **Report:** `reports/cm6_observational_results.json`
- **Reproduce:** `.venv/bin/python data/scripts/run_cm6.py`

### C-009 — CM-6 identifiability audit (L0, design-only)
- **Value:** `analysis_7_identifiability`: **n_candidate_edges = 84, n_identifiable = 0,
  n_not_identifiable = 84** (every backdoor-blocking set requires ≥1 unobserved node).
- **Report:** `reports/cm6_observational_results.json`
- **Decision:** `CM6_OBSERVATIONAL_ONLY_NO_IDENTIFICATION` (enforced).

### C-010 — CM-7 public-intervention method validation (L6)
- **Value:** primary ATE = **−0.0386**; exact 2-phase randomization p = **0.0733**;
  20-subset robustness p = 0.0754; list-level 95% CI **[−0.079, 0.002]**; subject-level
  [−0.087, 0.011]. Integrity 3328/3330 (99.94%); 0 x-precedes-y violations; 0 y-negative.
  Destructive controls NC1/NC2/NC4 ~0. Leakage audit PASS.
- **Data:** ds005494 v1.0.1, 20 subjects, 26 sessions, 3,330 pairs, 216 encoding-stim lists.
- **Report:** `reports/cm7_results.json`
- **Interpretation:** the **method** is validated as a causal-inference instrument; the
  **specific effect** is a valid null. Site-specific, train-specific, clinical iEEG, no sham.

### C-011 — CM-8R pre-human hardening (L0, no human data)
- **Values:**
  - Clean-room re-fit **bit-identical** to the frozen forecaster (SHA-verified).
  - Ghost pilot BRP_control held-out TEST = **0.0785** (target 0.10), 118 ghost participants,
    5,964 forecasts, 0 missing events, runtime 15.4 s.
  - Monte Carlo type-I calibrated at α=0.05 (not a finite-B artifact).
  - Realtime engine offline + transactional; total critical path **p95 = 478.0 ms**,
    cold first trial **876.5 ms** (encode p95 102 ms, BRP p95 76.7 ms).
  - Chaos **7/7** faults handled loudly; privacy **12/12** tests pass.
  - Readiness **10/10** gates → `CM8R_PREHUMAN_HARDENED`.
- **Reports:** `reports/cm8r_*/` (ghost_pilot, monte_carlo, realtime_engine, latency,
  failure_injection, privacy, cleanroom, readiness)
- **Reproduce:** `.venv/bin/python data/scripts/cm8r_cleanroom.py`,
  `.venv/bin/python data/scripts/cm8r_readiness.py`

### C-012 — CM-9A synthetic Oracle lab (L0, synthetic, no human data)
- **Value:** 4 oracle conditions (HIDDEN/REVEAL/VETO/REDIRECT) × 11 agent policies (O0–O10);
  300 steps × 20 seeds; baseline self-pred error 3.93. HIDDEN+O5 RPR = **1.48** (least
  predictable); VETO+O0 RPR = **0.16** (most predictable). Probes: computational
  irreducibility (O10), game-theoretic best response (O7).
- **Report:** `reports/cm9a_oracle_lab/cm9a_oracle_lab.json`
- **Reproduce:** `.venv/bin/python data/scripts/cm9a_oracle_lab.py`

## Frozen artifact hashes (from `docs/releases/cm8_prehuman_v1.md`)

| artifact | SHA-256 |
| --- | --- |
| `artifacts/cm8_forecaster/config.json` | `dbcbe443b6b09a3a33b53cfc1e1f6179a804cb3cef2ee8991444a7089e0cbd6a` |
| `artifacts/cm8_forecaster/ridge_weights.npz` | `7b13d52ce520d15793814d3a10b6269a21cc3d54e0e7dfce20d206fb2c0ed094` |
| `artifacts/cm8_forecasting_freeze_manifest.json` | `21bb0bb8c0789772ff47a5d3d1e6e17721088bd86f3b8fa2a5cfa4cce3e29b06` |
| `data/manifests/cm8_randomization_manifest.json` | `c6bcd84d7603d0a8e88e3cfdb005cab2a291b9f95ad24d158d9f417e4436032d` |
| `data/manifests/cm2_split_seal.json` | `6bac3b4c432bbc42bb5a6ff95e2e5abaa47b5b5cd90e80a15d2c947cea635bd4` |

## Rules enforced

- No claim is worded above its level (L0–L8).
- No free-will claim is made or implied.
- Negative results (C-005, C-006, C-009, C-010 effect) are reported as results, not reopened.
- Causal language (L6) is used only where a valid randomized identification exists (C-010 method).
