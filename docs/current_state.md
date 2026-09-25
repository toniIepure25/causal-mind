# Current State

## Project state

`CMREPO_EXPERT_GRADE_READY` (2026-09-25) — CM-REPO professionalized the repository
(engineering/governance only; **no scientific change**). Added: full architecture audit
(P0-P3, no P0); centralized path discovery + scientific constants (read from frozen
configs); domain error taxonomy + stable exit codes + run IDs + structured logging; a
research CLI (`cm doctor/validate/claims/artifacts/security/demo/reproduce`); a
human-data guard wired into the pre-commit hook + CI; removal of dead modules; the
`eval<->forecast` import cycle broken + an enforced import-boundary test; architecture,
governance (versioning, release, data classification, env-var registry, threat models,
SECURITY, CHANGELOG), runbooks (maintainer, new dataset/experiment/claim, protocol
amendment), a docs index + glossary, a rewritten professional README, a critical code
review (found + fixed a real `TfidfEncoder.fit` bug), and a project-health scorecard.
Full validation: `cm validate --with-tests` 8/8, `validate_project.sh` PASS,
`cm reproduce cm8` PASS (CM-8 no-drift), 12/12 frozen artifacts SHA-verified, lint ratchet
32/32 ruff + 93/93 mypy, clean tree. The scientific state below is UNCHANGED; no human
data; no CM-8 protocol change; no reinterpretation; no result shopping. Non-blocking
follow-ups F2-F7 tracked in `reports/cm_repo_scorecard.md`.

`CMLAB_SCIENTIFIC_DEEP_DIVE_COMPLETE` (2026-09-24) — the CM-LAB scientific deep dive
(sections 25-88) rigorously attacked the remaining assumptions of the CM-2/CM-3
predictive-dynamics finding, all on the frozen ds006067 split (83/18/17) with TRAIN-only
fitting and no human data. New claims C-102..C-107; C-101 revised. Decisions:
- **CMXVAL_PARTIAL_REPLICATION** (C-101 revised): subject-level gain survives at all horizons,
  but the gain is driven by SUBJECT IDENTITY (N0/N5 rejected), not temporal/transition
  structure (N1-N4, N6 not rejected).
- **CMUNC_WEAK** (C-102): confidence gating is unreliable (weak/anti-calibrated) - do NOT use
  for human Oracle work.
- **CMREP_PARTIAL** (C-104): the finding is representation-dependent (semantic MiniLM/mpnet >>
  lexical TF-IDF/NMF, 5.9x effect-size ratio).
- **CMPERS_NULL** (C-103): personalization actively HURTS (all gains negative).
- **CMDYN_LINEAR_PREDICTION_DOMINANT** (C-105): linear model captures most accessible structure;
  trajectory highly dynamic; higher local entropy predicts worse forecasting.
- **CMERR_WEAKLY_PREDICTABLE** (C-106): dominant large-error mode is NOVELTY (rare state, abrupt
  jump); pre-forecast error prediction weak (best AUROC 0.585).
- **CMORACLE_SELECTIVE_ONLY** (C-107): modest selective oracle (top-10% -> +0.039) but UNSTABLE
  under recursive rollout (L0->L3 degradation 0.092) - use selective + NON-recursive for CM-8P.
Standards: **CMLEAK_PASS** (new data-leakage scanner, L1-L5, all 7 scripts); **CMSTD_IN_PLACE**
(S50-59 mapped to runnable tools + PR checklist). **CMLAB_DISASTER_RECOVERY_REPRODUCED**
(second independent run; fixed a safe.directory fragility). **CM8_CONFIRMATORY_INTACT**
(CM-8 no-drift: config, freeze, code SHAs, randomization, registry all intact). Net scientific
picture: the predictive-dynamics finding is REAL but (a) subject-identity-driven, (b)
representation-specific (semantic), (c) not personalizable, (d) weakly confidence-gateable, and
(e) oracle-usable only in a selective, non-recursive mode. NO change to C-001..C-012, the frozen
CM-8 protocol, or the cm8-prehuman-v1.0 release; NO human data; NO result shopping; negative
results reported. The human experiment remains gated on supervisor sign-off + ethics (deadline
5 Oct 2026) + pilot authorization. No free-will claim.

`CMLAB_PROFESSIONAL_RESEARCH_PLATFORM_READY` (2026-09-21) — CM-LAB turned CAUSAL MIND into a professional, reproducible, portable research operating system on top of the immutable `cm8-prehuman-v1.0` freeze. Built: reproducible environment (S4), one-command validation + lint/type ratchet (S6), 10 scientific invariants (S7), claim graph with full traceability (S8), data lineage + artifact + experiment registries (S9-11), CI (S12), validation profiles + recovery runbook (S13/S14), disaster-recovery test (S60/61), and a security audit + standards (S75-84). Target states achieved: CMLAB_RESEARCH_OS_PASS, CMLAB_DISASTER_RECOVERY_PASS, CMLAB_CLAIM_TRACEABILITY_PASS, CMLAB_SECURITY_PASS, plus the first external-validation decision. CM-XVAL-1 (S16/S18-24) externally validated the CM-2/CM-3 predictive-dynamics finding on Open Play (openESM 0075, Zenodo 10.5281/zenodo.17536656): the model beats the strongest frozen baseline at every horizon (gain +0.016..+0.034, CIs exclude 0) but the target-shuffle permutation is not significant (p=0.71) -> `CMXVAL_PARTIAL`, recorded as NEW claim C-101 (L3). NO human data; NO change to C-001..C-012, the frozen CM-8 protocol, or the `cm8-prehuman-v1.0` release; NO result shopping. The human experiment remains gated on supervisor sign-off + ethics (deadline 5 Oct 2026) + pilot authorization. No free-will claim.

`CMPUB_SUPERVISOR_HANDOFF_READY` (2026-09-21) — pre-human freeze `cm8-prehuman-v1.0`
(git `8a9d5dd`). CM-PUB (2026-09-21) turned the completed program into a publication-ready,
supervisor-handoff package: pre-human release freeze + tag, master summary, claim-level
evidence matrix, supervisor package (one-pager, technical brief, 4 thesis options, pitch,
contact package, questions), 3 paper drafts + Oracle theory outline, science docs (novelty,
limitations, negative results, known/unknown, roadmap), claim-language linter (0 BLOCK /
8 WARN / PASS), publication + statistical + reproducibility + consistency audits, reviewer
simulation + response bank, venue landscape, thesis timeline, pilot handoff, README rewrite,
repo hygiene audit, CITATION.cff, license/data-use audit. NO human data; NO change to the
frozen CM-8 confirmatory protocol; NO optimization from simulation; NO reopening of closed
phases. The ONLY remaining work is the human experiment, gated on supervisor sign-off,
ethics approval (submission deadline 5 Oct 2026), and the pilot. No free-will claim.

Underlying research state: `CM8R_PREHUMAN_HARDENED` (2026-09-20)
(CM-1 = `CM1_PASS`; CM-2 = `CM2_PASS`; CM-3 = `CM3_PASS`; CM-5 = `CM5_NULL`;
CM-6 = `CM6_OBSERVATIONAL_ONLY_NO_IDENTIFICATION`; CM-7 =
`CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT` (CLOSED, pushed, C-010 L6); CM-8 =
`CM8_ETHICS_PACKAGE_READY`; CM-8R = `CM8R_PREHUMAN_HARDENED` (10/10 gates pass);
CM-9A = `CM9A_SYNTHETIC_ORACLE_READY`. The project has moved from FORECAST to
EXPLAIN/INTERVENE. CM-7 (2026-09-17) validated the intervention framework on
ds005494 (valid null; method validated). CM-8 (2026-09-17) is the first own
experiment (Pre-Oracle / Break-the-Chain): a within-subject randomized
CONTROL/SHAM/GENERAL-REDIRECT/SPECIFIC-CUE test of causal redirection of a PREDICTED
semantic trajectory, primary outcome BRP. All data-independent gates G1–G8 passed;
final statistical audit (type-I at α=0.05 = 0.047, independently reproduced →
CALIBRATION PASS); supervisor-ready University-of-Vienna ethics package produced
(docs/ethics/); software frozen (manifest); dry run ALL PASS (no human data).
CM-8R (2026-09-20) is the PRE-HUMAN HARDENING of the CM-8 confirmatory experiment
(NO human data): the participant-facing forecaster is frozen + reproducible
(clean-room bit-identical), the ghost pilot passes, the Monte Carlo is calibrated,
the realtime engine is offline + transactional + chaos-tested, the randomization is
audited, privacy is hardened, and the synthetic Oracle lab is ready. The ONLY
remaining blockers to human data are the EXTERNAL ones: supervisor sign-off, ethics
approval, and the pilot. NOT THE ORACLE. No free-will claim.)

## 2026-09-14 handoff recovery (git)

- Previous session was lost to a context limit; unpushed pod commits `ea69195`
  (CM-5A selective OpenNeuro acquisition + real-data minimal smoke) and `5e88f72`
  (gitignore-data-neural) were preserved in `/home/jovyan/work/cm5a_push.bundle`
  (base `9c59300`, verified).
- Integrated through the authorized orchestrator bundle workflow (workstation
  clone of GitHub main `76066ac` -> merge of pod main `5e88f72` -> push).
  **GitHub main is now `a61753c`.** Pod main fast-forwarded to `a61753c`.
- Handoff integrity verified on pod: 112/112 tests pass (requires
  `HF_HOME=/home/jovyan/work/.hf-home`), ruff clean.
- The pod was recreated between sessions (now
  `orchestraiq-jupyter-ccd58f4b9-jbqtj`); the PVC `/home/jovyan/work` is intact.
  Node v20.11.1 restored at `/home/jovyan/work/.local/node`; `@openneuro/cli`
  4.30.2 + deps reinstalled at `causal-mind-v2/.tools/openneuro` (gitignored);
  the fetcher runs with
  `NODE_PATH=/home/jovyan/work/causal-mind-v2/.tools/openneuro/node_modules`.
- sub-001/sub-005 neural files re-verified after the pod recreation: all six
  large files (2 BOLD, 2 confounds TSV, 2 masks) HASH_MATCH their annex keys.
- OpenNeuro authenticated access verified healthy (snapshot tree API + URL
  resolution, no credential exposure).

## Current stage

Phase 2: CM-1 (data), CM-2 (non-neural next-thought prediction), CM-3
(multi-step cognitive futures / Thought Predictive Horizon), and CM-5 (neural)
complete and pushed. CM-5 decisive result: a clean NULL — HRF-safe BOLD
contains no incremental prospective value for future thought beyond the
frozen behavioral-history model + motion/speech confounds (h=1,3,5,10;
N1-N3 ladder; red-team GO).

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
- **CM-3 (L5):** cognitive history predicts **future** thought semantics T[t+h]
  above the strongest frozen baseline at **every** event horizon h=1..10, with a
  smooth monotonic decay of PredictiveGain (+0.0349 at h=1 → +0.0044 at h=10, all
  95% CIs excluding 0). **TPH_semantic ≥ 10 thoughts (~2 min)** — a lower bound,
  since the gain is still significant at the max tested horizon. Subject-disjoint
  (83/18/17 sealed), reproduced exactly; survives time-shuffled,
  transition-destroyed, and a stronger random-target null (p=0.0000). History
  depth saturates at k≈3; the predictive window is ~2 min in wall-clock time.
  Effect modest; small test set (n=17); no causal claim. Red-team GO.

## Failed hypotheses

(none yet — CM-2 and CM-3 are modest positives, not nulls)

## Active tasks

- CM-5 MRI-eligible cohort: metadata-first audit of all 118 subjects
  (availability + cheap confound/QC metadata only, NO neural outcomes),
  then freeze/seal eligibility, project the frozen CM-3 split, seal the cohort,
  and acquire eligible BOLD only.
- CM-5 decisive analysis (M0-M4, M4-M2 + residual test, NC1-NC6), red-team,
  claims decision.
- Optional CM-3 extensions (only if warranted): nonlinear/deep multi-horizon
  heads (justified only if they beat the linear model on held-out data); finer
  TPH resolution beyond h=10.

## CM-5 (neural) — COMPLETE: clean NULL (no incremental neural value)

- **Status:** `CM5A_REAL_DATA_SMOKE_PASS`. OpenNeuro access restored via an
  authenticated selective acquisition route (API token configured on the pod,
  chmod 600, never printed/committed). Custom selective fetcher
  `scripts/cm5_fetch.js` enforces the hard invariant
  **requested dataset path == resolved S3 URL path** (mismatch => SKIP); the
  OpenNeuro API path-mismatch anomaly (e.g. requested `sub-001 ... bold.json`
  resolved to a `sub-127` object) is documented and regression-tested. Affected
  in-Git JSON files were sourced from the authoritative Git metadata clone
  (`/home/jovyan/work/ds006067_git`).
- **Real data on disk (gitignored `data/neural/`):** sub-001 + sub-005 MNI BOLD
  (~771 MB / ~791 MB), confounds TSV, brain masks, BOLD + confounds JSONs —
  all HASH_MATCH against annex keys (re-verified 2026-09-14).
- **N=2 real-data smoke:** the full pipeline (OpenNeuro BOLD -> confounds ->
  HRF-safe windows -> neural features -> M0-M4) ran end-to-end on
  sub-001/sub-005 (211 event rows; M2=0.8847, M4=0.8482, gain=-0.0365).
  **ENGINEERING SMOKE ONLY** — zero scientific interpretation; excluded from
  model selection, QC-threshold tuning, and all confirmatory decisions.
- **Frozen/sealed protocol** (`docs/protocol/cm5_frozen_protocol.md`, seal in
  `data/manifests/cm5_protocol_seal.json`): HRF-safe buffer B=6 s, neural
  window W=15 s, TR~1.5 s; primary alignment C (lagged neural history with HRF
  buffer); horizons h=1,3,5,10; models M0-M4; decisive contrast M4 vs M2 +
  mandatory residual test; negative controls NC1-NC6; subject-disjoint;
  subject-level inference (bootstrap/permutation); gates N0-N6.
- **Decisive result (2026-09-14):** MRI-eligible cohort (106 subjects,
  73/17/16 after F2 tSNR + alignment gates) acquired (87.5 GB BOLD,
  hash-verified). IncrementalNeuralGain (M4-M2) negative at every horizon
  (primary N2: -0.088/-0.085/-0.085/-0.090, CIs exclude 0, 0/16 positive);
  N1~0/N3~-0.016/N2~-0.085 ladder; NC4->0; controls confirm no shortcut.
  CM5_NULL_NO_INCREMENTAL_NEURAL_VALUE (claim C-005, L5 negative).
- **Prior next (done):** define the MRI-eligible cohort WITHOUT inspecting
  neural prediction outcomes (criteria: data availability, file validity,
  temporal compatibility under B=6s/W=15s, imaging/motion QC, behavioral
  compatibility); download only cheap confound/QC metadata first; freeze +
  hash-seal eligibility criteria BEFORE decisive outcomes; project the frozen
  CM-2/CM-3 split (83/18/17) onto eligible subjects; produce the CM5 MRI COHORT
  SEAL; verify storage; then acquire sealed-eligible BOLD only.

## CM-7 (public intervention method validation) — COMPLETE: valid NULL

- **Status:** `CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT` (claim C-010, L6; method
  validated, null causal effect). Red-team GO-WITH-CHANGES (all 4 changes applied).
  **CLOSED and pushed to GitHub** (main = `6fdd05b`, 2026-09-17; freeze `207fce0` in
  history). Immutable except for genuine reproducibility fixes.
- **What it validated:** that the CAUSAL MIND intervention framework correctly
  identifies and estimates an experimentally-identified causal effect
  `P(Y_future | do(X))` in an independent public dataset — a method-validation
  bridge (FORECAST -> INTERVENE), NOT a claim that "hippocampal stimulation
  enhances memory."
- **Dataset:** ds005494 (Herrema & Kahana, CC0, v1.0.1; N=20, 26 sessions, 555
  lists; 216 encoding-stim). Open-loop stimulation of a targeted
  hippocampal/entorhinal electrode at encoding -> cued recall. List-level
  within-subject randomization (10 enc-stim / 10 ret-stim / 5 no-stim; alternating
  phase 50/50). Minimal acquisition: 26/26 `beh.tsv` (no iEEG), SHA-256 manifest.
- **Primary result:** site-specific ATE (stim vs no-stim pairs within encoding-stim
  lists) = **-0.0386**; exact 2-phase randomization p = **0.0733** (20-subset
  robustness p = 0.0754); list-level bootstrap 95% CI [-0.079, 0.002];
  subject-level (nesting-aware) CI [-0.087, 0.011]. **counterfactual_status =
  experimentally_identified.** Corroborating list-level contrast -0.0080 (p=0.712);
  latency null (p=0.163); semantic CTE 0.046 (negligible). A small NEGATIVE effect
  down to ~-0.079 is not excluded; positive effects are ruled out.
- **Method validation (the point):** leakage audit PASS (no post-treatment variable
  in the adjustment set; retrieval-stim excluded from the future-state estimand;
  list/subject-level inference); destructive controls NC1/NC2/NC4 ~0 (the machinery
  does not hallucinate effects); serial-position confound canceled by balanced phase
  (start-on=109, start-off=107; imbalance term -0.0004); integrity 3328/3330
  (99.94%), 0 missing official outcomes.
- **Caveats:** 14/26 sessions truncated (recording ended early; does not bias the
  within-list ATE); clinical iEEG population; no sham control; retrieved (cued)
  semantic state, not a free thought state.
- **Deliverables:** `docs/cm7_protocol.md` (frozen), `docs/cm7_identification.md`,
  `docs/datasets/ds005494_audit.md`, `docs/cm7_final_report.md`,
  `data/scripts/cm7_analyze.py`, `data/scripts/cm7_download.sh`,
  `data/manifests/ds005494_manifest.json`, `reports/cm7_results.{json,md}`.
- **Next:** CM-8 (Pre-Oracle / Break-the-Chain own experiment, IRB-gated) — the
  first own experiment (E8 voluntary redirection), NOT THE ORACLE.

## CM-8 (Pre-Oracle / Break-the-Chain) — ETHICS PACKAGE READY

- **Status:** `CM8_ETHICS_PACKAGE_READY` (all data-independent gates G1–G8 satisfied;
  supervisor-ready University-of-Vienna ethics package produced; the only blocker to human
  data is supervisor sign-off + ethics approval + the pilot). NOT THE ORACLE — the
  participant is not shown the exact prediction.
- **Statistical audit (final):** primary test is two-sided α=0.05 (SEPARATE from the
  basin tail 0.10). Type-I error at α=0.05 = **0.047** (MC 95% CI [0.013, 0.080]);
  independently reproduced (alt-seed 0.040) → **CALIBRATION PASS**. The earlier cited
  0.113 was the type-I error at the 0.10 level (basin tail / test level had been conflated)
  — NOT the α=0.05 type-I error. BRP calibration correct (0.0989 ≈ 0.10); recovery bias
  < 0.003.
- **Ethics package (docs/ethics/):** frozen protocol (`cm8_research_plan.md` v1.0),
  participant information + consent (lay language, no sensational terms), GDPR data-
  protection plan (pseudonymized ≠ anonymous), risk assessment, recruitment (Vienna
  Cognitive Science Hub readiness), debrief, compensation (amount = HUMAN INPUT REQUIRED),
  final preregistration (`cm8_preregistration_final.md`), U-of-Vienna application answers
  (institutional fields = HUMAN INPUT REQUIRED), submission checklist, software-freeze
  manifest (SHAs/config hashes), dry-run report (ALL PASS, no human data).
- **Software freeze:** `docs/ethics/cm8_software_freeze_manifest.json` (basin/estimator/
  power/dry-run/randomization SHAs + config); randomization manifest frozen
  (`data/manifests/cm8_randomization_manifest.json`); forecasting-model SHA = placeholder
  (G8, frozen at pilot/confirmatory boundary).
- **Submission authority:** for a Master's thesis, the **supervisor / responsible study-law
  body** submits to the University of Vienna Ethics Committee (deadline 5 Oct 2026 for the
  5 Nov 2026 meeting). The researcher prepares; does NOT submit.
- **North-star:** can a deliberate or externally-induced intervention CAUSALLY REDIRECT a
  PREDICTED semantic trajectory?
- **Design (CM-8A):** within-subject randomized 4-condition experiment — CONTROL / SHAM /
  GENERAL REDIRECT (endogenous) / SPECIFIC CUE (exogenous). Primary = BRP (P(observed
  future leaves the frozen predictor's predicted-future basin | intervention)); ATE_GENERAL
  and ATE_CUE estimated separately vs pooled CONTROL/SHAM (SHAM-alone sensitivity);
  subject-clustered permutation test; N=20 (24 trials) for 80% power at Δ≈0.11.
- **BRP/basin (CM-8B):** predicted-future basin = ball around the frozen forecast with
  radius = held-out 90th-pct prediction-error norm (prospective, not tuned to outcomes);
  `src/causal_mind/causal/predicted_basin.py`.
- **Estimator validation (CM-8D, G2 PASS):** `data/scripts/cm8_synthetic.py` — H0 type-I
  error 0.113 (≈α), known effects recovered (bias < 0.007).
- **Power (CM-8E, G4 PASS):** `data/scripts/cm8_power.py` — ICC 0.2, N=20 → 80% power for
  Δ≈0.11; larger effects need fewer.
- **Platform (CM-8C):** `docs/cm8_realtime_platform.md` (outcome engine reuses the CM-6/
  CM-8B machinery; capture/UI decided after the pilot modality).
- **Prereg + SAP (CM-8F) + Ethics (CM-8G):** `docs/cm8_preregistration.md`,
  `docs/cm8_ethics.md` (privacy-by-design for sensitive thought streams).
- **Red-team (G7):** self GO-WITH-CHANGES (5 fixes) + independent REVIEWER confirmatory
  pass GO-WITH-CHANGES (primary estimands clean; endogenous-vs-exogenous contrast + CUE
  priming disclosed as confounded/secondary). `docs/review/cm8_redteam.md`.
- **Deliverables:** `docs/cm8_dag.md`, `docs/cm8_basins_brp.md`,
  `docs/cm8_experiment_design.md`, `docs/cm8_preregistration.md`, `docs/cm8_ethics.md`,
  `docs/cm8_realtime_platform.md`, `docs/research/cm8_literature_audit.md`,
  `docs/review/cm8_redteam.md`, `src/causal_mind/causal/predicted_basin.py`,
  `data/scripts/cm8_synthetic.py`, `data/scripts/cm8_power.py`.
- **Next:** ethics/IRB submission (CM-8G package) → pilot (CM-8P, gated) → confirmatory
  (CM-8H, gated). Oracle (CM-9) remains gated.

## CM-8R (Pre-Human Hardening) — COMPLETE: CM8R_PREHUMAN_HARDENED (2026-09-20)

- **Status:** `CM8R_PREHUMAN_HARDENED` (10/10 readiness gates pass; pushed to GitHub
  main = `a15cbc5`). NO human data collected; NO change to the frozen CM-8 confirmatory
  protocol (Workstream A). Workstream B per `docs/cm8r_confirmatory_boundary.md`.
- **Readiness scorecard (10/10):** CM8R_GHOST_PILOT_PASS, CM8R_MONTE_CARLO_PASS,
  CM8R_REALTIME_ENGINE_PASS, CM8R_RANDOMIZATION_PASS, CM8R_PRIVACY_PASS,
  CM8R_CHAOS_PASS, CM8R_REPRODUCIBILITY_PASS, CM9A_SYNTHETIC_ORACLE_READY,
  CM8R_FORECASTER_FROZEN, CM8_CONFIRMATORY_INTACT.
- **Forecasting freeze (S3):** `LinearMultiHorizon` (k=3, α=100, horizons 1-10) fitted on
  CM-2 TRAIN (83 subjects, seal verified); basin r_alpha calibrated on VAL (h*=2: r=0.9911).
  Weights = 28MB `.npz` (gitignored, SHA in manifest). `artifacts/cm8_forecasting_freeze_manifest.json`.
- **Ghost pilot (S2):** `CM8R_GHOST_PILOT_PASS`. Prospective replay of ds006067 through the
  frozen forecaster. BRP_control held-out TEST = 0.0785 (target 0.10); forecast repro exact;
  deterministic replay; crash recovery; latency p95 = 0.21 ms.
- **Synthetic world (S4):** `src/causal_mind/sim/` — 21 scenarios S0-S20 with ground-truth
  causal parameters; the frozen ATE + subject-clustered permutation estimator.
- **Monte Carlo (S5):** `CM8R_MONTE_CARLO_PASS`. Type-I under the null (S0) = 0.080 (n=300);
  a B-check (B=200/1000/5000 → 0.042) confirms it is MC noise, NOT a finite-B artifact.
  Power/bias per scenario reported.
- **Randomization red team (S16):** `CM8R_RANDOMIZATION_PASS`. Perfect balance, max run 1,
  deterministic; the fixed permutation is predictable BY DESIGN (mitigation = blinding).
- **Power surface (S6):** grid over N (12-60), trials (12-48), ICC, effect; power rises with
  N more than trials; high ICC reduces power. The frozen N=20 is under-powered for small
  effects (documented, not changed).
- **BRP red team (S7):** 9 adversarial cases; 7/9 produce a misleading high BRP (magnitude-
  only change, lexical echo, tiny-basin miscalibration, volatility). Secondary diagnostics
  (cosine-direction, Mahalanobis, persistence, novelty) reveal the modes. BRP stays PRIMARY.
- **Basin robustness (S8/9):** BRP_control stable across percentiles (0.03-0.17) and
  dimensions (0.08-0.12); global vs subject-calibrated basins are similar.
- **Realtime engine (S10-15):** `src/causal_mind/engine/` — OFFLINE (no Qwen/LLM/internet),
  transactional (append-only JSONL, atomic finalization, no duplicate finalization),
  event timestamps (wall-clock UTC + monotonic), full trial lifecycle. `CM8R_REALTIME_ENGINE_PASS`.
  Latency: total p95 ~478 ms, cold max ~876 ms. Chaos: 7/7 faults handled loudly
  (`CM8R_CHAOS_PASS`).
- **Privacy (S23-25):** `src/causal_mind/privacy/` — PII/sensitive-content detection (13
  categories) + redaction; data minimization (embeddings, not raw text); pseudonymization
  (salted hash, encrypted salt); encryption at rest; access audit; complete deletion; no
  remote telemetry / no external LLM. `CM8R_PRIVACY_PASS` (12/12).
- **Clean-room reproduction (S26/27):** `CM8R_REPRODUCIBILITY_PASS`. The forecaster weights
  SHA matches the manifest; the split seal verifies; a CLEAN-ROOM re-fit from source + data
  is BIT-IDENTICAL to the frozen artifact. Artifact hash manifest = the reproducibility anchor.
- **Analysis (S17/18/21):** sham ATE ~0 (believable no-op); cue effect partly a lexical echo;
  burden ~28 min / 96 thoughts (feasible).
- **Operational design (S19/20/22/28/29):** manipulation check, report-reactivity, pilot
  GO/ITERATE/STOP (operational, not the ATE), analysis blinding, experimenter blinding.
  `docs/cm8r_operational_design.md`.
- **Publication plan (S30-32):** Paper 1 (forecasting), Paper 2 (causal inference), novelty
  matrix. `docs/cm8r_publication_plan.md`.
- **CM-9A synthetic Oracle lab (S33-42):** `src/causal_mind/oracle/` — 4 conditions
  (HIDDEN/REVEAL/VETO/REDIRECT), 11 policies (O0-O10), RPR/PIE metrics. `CM9A_SYNTHETIC_ORACLE_READY`.
  VETO+O0 most predictable (RPR=0.16); HIDDEN+O5 least (RPR=1.48).
- **Deliverables:** `src/causal_mind/{sim,engine,privacy,oracle}/`, `data/scripts/cm8r_*.py`,
  `data/scripts/cm9a_oracle_lab.py`, `reports/cm8r_*/`, `reports/cm9a_oracle_lab/`,
  `docs/cm8r_confirmatory_boundary.md`, `docs/cm8r_operational_design.md`,
  `docs/cm8r_publication_plan.md`, `artifacts/cm8_forecaster/`.
- **Next:** the EXTERNAL blockers only — supervisor sign-off, ethics approval, the pilot
  (CM-8P, gated). Then the confirmatory run (CM-8H, gated). Oracle (CM-9) remains gated.

## Blockers

- **Token lifecycle:** Run:ai CLI tokens expire ~daily; refresh tokens do NOT
  auto-renew in the CLI. When the token expires, a human must complete
  `runai login remote-browser` (open URL, paste code). Runbook:
  `docs/runbooks/qwen_tunnel.md`. The pod-side helper
  `scripts/runai_login_pty.py` stages the flow and waits for the code in
  `/tmp/runai-code.txt`.

## Key commit hashes

- `a15cbc5` **GitHub main after CM-8R push (2026-09-20)** — CM-8R pre-human hardening
  (CM8R_PREHUMAN_HARDENED, 10/10 gates) + CM-9A synthetic Oracle lab; pushed
  `b77d5f9..a15cbc5 main -> main`, verified on the remote.
- `b77d5f9` GitHub main after the first CM-8R push (2026-09-20) — forecasting freeze +
  ghost pilot + Monte Carlo + randomization + power surface + BRP red team + basin
  robustness + realtime engine + chaos + privacy.
- `feb3257` GitHub main after the CM-8E ethics freeze (2026-09-19) — CM8_ETHICS_PACKAGE_READY.
- `6fdd05b` **GitHub main after CM-7 push (2026-09-17)** — CM-7 valid NULL (C-010, L6);
  pushed `08456c7..6fdd05b main -> main`, verified on the remote.
- `207fce0` CM-7 protocol freeze + identification + authoritative ds005494 audit
  (in the pushed history).
- `08456c7` previous GitHub main (CM-6).
- `a61753c` GitHub main after CM-5A integration (2026-09-14 handoff recovery)

## Exact reproducibility commands

```bash
# on the pod, via SSH as jovyan (sidecar netns)
cd /home/jovyan/work/causal-mind-v2
export PATH=/home/jovyan/work/.local/node/bin:$PATH
export NODE_PATH=/home/jovyan/work/causal-mind-v2/.tools/openneuro/node_modules
export HF_HOME=/home/jovyan/work/.hf-home
scripts/qwen_tunnel_supervisor.sh status
.venv/bin/python -m causal_mind.cli status
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests scripts
node scripts/cm5_fetch.js --dry --subject=sub-001 --no-optional
```

## Environment notes

- Working root: `/home/jovyan/work/causal-mind-v2` (jovyan-owned). The original
  `/home/jovyan/work/causal-mind` is a frozen root-owned snapshot (NFS ownership
  split).
- Worktrees: `/home/jovyan/work/worktrees/causal-mind-v2/<worker>`.
- All git commands need `safe.directory=*` (NFS maps ownership to uid 65534);
  scripts and the planner set this automatically.
- The SSH session runs in a sidecar network namespace: the main container's
  127.0.0.1:18000 is NOT visible there. The tunnel supervisor binds the
  port-forward inside the SSH netns; the cluster gateway is reachable directly
  via `cisco-ai-pod.cc-demos.com` (no Caddy needed).
- Pod recreated 2026-09-13/14 (`orchestraiq-jupyter-ccd58f4b9-jbqtj`);
  ephemeral rootfs contents (system node, npm globals) were lost and restored
  onto the PVC (`/home/jovyan/work/.local/node`,
  `causal-mind-v2/.tools/openneuro`). The HF cache used by the MiniLM test is
  `/home/jovyan/work/.hf-home` (set `HF_HOME` accordingly).
