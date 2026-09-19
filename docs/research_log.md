# Research Log (chronological)

## 2026-09-09

- **Infrastructure audit.** Pod `orchestraiq-jupyter-5d6c688775-fbxj5` (namespace
  `runai-romania-dev`): A100-SXM4-40GB idle, 256-core node, ~1 TiB RAM, 107 TB free NFS
  at `/home/jovyan/work`, Python 3.13 (system) / 3.11 (uv), PyTorch 2.11.0+cu128,
  CUDA 12.8 driver. SSH via node IP `10.130.123.35:32516` (LoadBalancer IP is
  firewalled from the workstation).
- **Qwen endpoint discovered and restored.** Existing Run:ai workload
  `qwen38-27b12` (`Qwen/Qwen3.8-27B-FP8`) reachable only through the runai CLI
  port-forward + Caddy tunnel previously built for `hotc2026-lab`. Tunnel supervisor
  restarted; `http://127.0.0.1:18000/v1` healthy; chat completion + tool-call smoke
  tests pass. Run:ai CLI token valid until 2026-09-10 (refresh token present; if
  refresh fails, human must re-run `runai login remote-browser` — documented blocker
  contingency).
- **Repository created** at `/home/jovyan/work/causal-mind`; orchestration infrastructure
  adapted from the proven `hotc2026-lab` harness (task queue with atomic claims,
  per-worker worktrees, supervisor loops, Qwen client); direct Qwen tool-loop agent
  harness added for autonomous workers.
- **CM-0 epistemic seal** drafted: questions, definitions, hypotheses H1-H6, validation
  protocol frozen, claims registry initialized.

## 2026-09-10

- **NFS ownership conflict discovered.** Files created via `kubectl exec` (root) are
  not writable from the SSH session (jovyan) and vice versa; the NFS maps everything to
  uid 65534 (nobody). The original root `/home/jovyan/work/causal-mind` (`.git`,
  `reports/agents`, worktrees) became locked for jovyan. Decision: rebuild at a
  jovyan-owned root `/home/jovyan/work/causal-mind-v2`; the old root is a frozen
  snapshot. All git commands now use `safe.directory=*` (dubious-ownership guard).
- **Rebuild completed.** Tree, dot-dirs (`.home`, `.runai-cli`, `.caddy`), agent
  reports, queue state, and worktree deliverables copied; fresh venv via uv
  (jovyan-owned cache `/home/jovyan/work/.uv-cache-jovyan`); 53/53 tests pass, ruff
  clean; git re-initialized; 5 worktrees recreated under
  `/home/jovyan/work/worktrees/causal-mind-v2/`.
- **Harness fixes.** (1) Agent loop now nudges the model on an empty final message
  instead of stopping (causal smoke had terminated with no output). (2) `cm status` /
  `cm qwen` CLI dispatch bug (missing `args` parameter). (3) Planner git calls and all
  scripts set `safe.directory=*`.
- **Qwen token expired (2026-09-10 11:03Z); refresh token did not renew.** The
  main-netns tunnel died. Discovered the SSH session runs in a sidecar network
  namespace (main container's 127.0.0.1:18000 not visible), but the cluster gateway
  `cisco-ai-pod.cc-demos.com` (10.130.240.221) is directly reachable from it, so the
  tunnel was rebuilt WITHOUT Caddy: plain `runai workspace port-forward` bound to
  127.0.0.1:18000 inside the SSH netns. New self-healing supervisor
  (`scripts/qwen_tunnel_supervisor.sh`, direct mode) running.
- **Re-authentication.** Human completed `runai login remote-browser` via
  `scripts/runai_login_pty.py` (pty wrapper that stages the flow, captures the URL,
  and delivers the pasted code from `/tmp/runai-code.txt`). New token written
  2026-09-10 20:59Z.
- **Phase C complete.** All six agents smoke-tested end-to-end: researcher (GO, 7
  cycles), data (GO, 5), forecasting (GO, 9), causal (GO, 23 — re-run after the
  empty-message fix), reviewer (GO, 6), orchestrator (GO, 10). All six SMOKE tasks
  reviewed and drained to done.

## 2026-09-14

- **Handoff recovery (git).** Previous session lost to a model context limit.
  Unpushed pod commits `ea69195` (CM-5A selective OpenNeuro acquisition +
  real-data minimal smoke) and `5e88f72` (gitignore-data-neural) were preserved
  in `/home/jovyan/work/cm5a_push.bundle` (base `9c59300`). Verified the bundle
  on the pod, cloned GitHub main (`76066ac`), merged pod main `5e88f72` into it
  (clean; no file overlap), and pushed. **GitHub main is now `a61753c`**; pod
  main fast-forwarded to the same SHA via a sync bundle (the pod repo has no
  GitHub remote by policy; pushes go through the workstation).
- **Handoff integrity check.** 112/112 tests pass on the pod (the MiniLM
  integration test needs `HF_HOME=/home/jovyan/work/.hf-home`); ruff clean.
- **Pod recreation discovered.** The pod was recreated between sessions
  (`orchestraiq-jupyter-ccd58f4b9-jbqtj`); the PVC is intact but the ephemeral
  rootfs lost the system node install. Restored node v20.11.1 at
  `/home/jovyan/work/.local/node` and reinstalled `@openneuro/cli@4.30.2` +
  `node-fetch@2` + `mkdirp` into the gitignored
  `causal-mind-v2/.tools/openneuro` (run with `NODE_PATH`).
- **Neural data re-verification.** All six large sub-001/sub-005 files
  (BOLD x2, confounds TSV x2, masks x2) re-hashed: all HASH_MATCH against the
  annex keys in `data/manifests/cm5_minimal_neural_files.tsv`.
- **OpenNeuro auth health.** Authenticated snapshot-tree API call succeeds
  (dry-run of `scripts/cm5_fetch.js`); the URL-path identity guard remains
  active (the known `bold.json` path-mismatch anomaly still reproduces and is
  skipped). No credentials exposed.
- **Next.** CM-5 MRI-eligible cohort: metadata-first audit of all 118 subjects
  (availability + cheap confound/QC metadata only), freeze + hash-seal
  outcome-independent eligibility criteria, project the frozen CM-3 split
  (83/18/17), seal the cohort, verify storage, then acquire eligible BOLD only.

## 2026-09-14 — CM-5 decisive analysis: clean NULL (no incremental neural value)

- **MRI-eligible cohort (outcome-independent).** Metadata-first audit of all
  118 subjects (availability + confounds QC + HRF-safe target counts). Frozen
  eligibility criteria (CM5-ELIG-1, hash-sealed): data availability (URL-path
  identity guard), file validity, >=20 steady-state HRF-safe targets (AM-1:
  onset>=36s), severe-motion screen (mean FD>1.0mm), behavioral compatibility.
  Excluded: sub-002 (OpenNeuro pointer-object anomaly, guard-fire), sub-067/
  087/110 (<20 targets), sub-089 (mean FD 1.207mm). Cohort 113 (79/18/16),
  sealed (reports/cm5_cohort_seal.json).
- **BOLD acquisition.** All 113 subjects' preproc BOLD + masks downloaded via
  the guarded, hash-verified, resumable fetcher (226 files, 0 mismatches, 0
  hash failures, 87.5 GB). Storage verified (87.5 GB vs ~102 TB free).
- **Post-acquisition gates (pre-registered, outcome-independent).** F2 tSNR
  gate excluded 6 (tSNR < 5th percentile; CM5-F2-TSNR-1). Cohort-level
  N-GATE-1 alignment audit found sub-036 with 2 OSF thoughts lacking a raw MRI
  event (CM5-ALIGN-1, excluded). Final cohort 106 (73/17/16).
- **Decisive result (CM5_NULL).** IncrementalNeuralGain (M4-M2) is NEGATIVE at
  every horizon h=1,3,5,10 for the primary N2 (Schaefer-400): -0.088/-0.085/
  -0.085/-0.090 (95% CIs exclude 0; 0/16 test subjects positive). Capacity
  ladder: N1 (7 nets) ~-0.001, N3 (PCA-50) ~-0.016, N2 (400) ~-0.085 — the
  degradation scales with dimensionality (noise signature, not a real signal).
  NC4 (nuisance-only) -> 0; NC1/2/3/5/6 preserve the negative gain (no
  correspondence to destroy). M0=0.32 (behavior), M2=0.32, M4=0.23.
- **Red-team: GO (conditional).** Fixed a CI-reporting bug (bootstrap_ci
  returns mean,lo,hi) and removed a post-cutoff speech feature (lag-to-next-
  onset). Confirmed no leakage (HRF-safe window, causal z-score, N3 fit on
  train only), the negative gain is expected Ridge noise (linear per-dim cost),
  and the null is strongest where power exists (N1/N3). Licensed claim is a
  scoped negative L5 result; NOT licensed: "brain has no prospective info"
  (underpowered for small high-dim effects), any causal/free-will claim.
- **Reproducibility.** 112/112 tests pass; synthetic end-to-end (injected
  neural signal) gives positive gain that collapses under all controls — the
  pipeline can detect a real signal.
- **Next.** Commit + push the CM-5 null. The neural incremental-value question
  is answered (null) for this task/window/horizons/baseline.

## 2026-09-16 — CM-6: Causal Genealogy (FORECAST -> EXPLAIN/INTERVENE)

- **Framing.** CM-5's frozen NULL (HRF-safe fMRI adds no incremental prospective value)
  motivates the transition from prediction `P(T_future | history)` to causation
  `P(T_future | do(X))`. Prediction != causation; CM-6 must not claim causal effects from
  observational association.
- **CM-6A (observational candidate SCM).** 118 subjects, 6436 thoughts; 14 GPT-rated
  dimensions + linguistic + temporal + semantic state. 7 analyses (lagged skill, CI
  structure, incremental value, transition asymmetries, cross-subject stability,
  mediator/moderator, identifiability audit). Result: **0/84 candidate edges causally
  identifiable** (unmeasured confounding). 39/272 CI edges survive BH-FDR; 0/126 mediator
  triples survive. **Red-team (CM-6J) found the "affect is strongest" headline is a
  between-subject GPT-rating-baseline artifact** (within-subject lag-1 R^2 0.01-0.05 vs
  pooled 0.05-0.20; GPT inflated vs human: joy +0.50, anxiety +0.27). Downgraded. The
  robust observational signal is the linguistic-load cluster (duration->gap r=0.828) and
  the semantic embedding.
- **CM-6B (public intervention dataset audit).** 16 candidates, 9 verified via S3/README.
  Best public `do(X)->future semantic state` = **ds005494** (E3 memory cue, N=20, iEEG,
  randomized open-loop stimulation). Closest affect handle = ds006583 (music->affect,
  N=43). **Gap: no public dataset tests voluntary redirection of a predicted thought (E8).**
- **CM-6D/E (causal machinery).** Metrics (CTE, BRP, persistence, divergence, decay) +
  SemanticBasin + matched-control sampler + a counterfactual engine that refuses to label
  an unidentified counterfactual as causal (enforced in code, 61/61 tests, ruff clean).
- **CM-6C/F/G/H/I (target ranking + experiment design + Oracle gate).** First public test
  = ds005494 (method validation). First own experiment = **CM-6H pre-Oracle** (voluntary
  redirection: CONTROL / SHAM / GENERAL REDIRECT / SPECIFIC CUE -> BRP), with CM-6J design
  fixes (sham-instruction demand control, cue-verbatim lexical-overlap rule, baseline-
  diversity floor, 4x4 Latin-square counterbalancing). THE ORACLE gated behind 6 unmet
  readiness criteria (CM-6I).
- **Red-team (CM-6J): GO-WITH-CHANGES.** No BLOCK-level leakage. All changes applied:
  affect downgrade, 3 factual doc errors fixed, BH-FDR added, CM-6H design fixes, CM-6
  claims registered (C-006..C-009).
- **Decision: CM6_OBSERVATIONAL_ONLY_NO_IDENTIFICATION** (CM-6A); the public test and the
  own experiment are designed, not executed (IRB required). Next: validate the method on
  ds005494, then seek IRB for CM-6H.

## 2026-09-17 — CM-7: Public Intervention Method Validation (ds005494): valid NULL

- **Goal.** Validate that the CAUSAL MIND intervention framework correctly recovers an
  experimentally-identified causal effect `P(Y_future | do(X))` in an independent public
  dataset — a method-validation bridge (FORECAST -> INTERVENE), NOT a claim that
  "hippocampal stimulation enhances memory."
- **Authoritative audit (RESEARCHER).** ds005494 (Herrema & Kahana, CC0, v1.0.1; N=20,
  26 sessions) is CONDITIONALLY IDENTIFIABLE (A1-A5): open-loop stimulation of a targeted
  hippocampal/entorhinal electrode at encoding (X, documented train: 50 Hz, 230 pulses,
  300 us, 4.6 s, onset -200 ms) -> cued recall (Y: `correct`/`resp_word`/`response_time`),
  list-level within-subject randomization (10 enc-stim / 10 ret-stim / 5 no-stim;
  alternating phase 50/50). Post-treatment iEEG/arousal/math-distractor/subjective state
  excluded from the adjustment set.
- **Minimal acquisition (DATA).** 26/26 `beh.tsv` (no iEEG, 6.4 MB) + participants +
  wordpool + dataset_description + sidecars; SHA-256 manifest. No credentials exposed.
- **Identification (CAUSAL).** `docs/cm7_identification.md`: A1-A5, estimand = site-specific
  ATE of encoding stimulation on cued recall (pair-level within enc-stim lists).
  Retrieval-stim (concurrent) kept out of the future-state estimand.
- **Protocol frozen BEFORE decisive outcomes** (`docs/cm7_protocol.md`, commit `207fce0`).
- **Primary analysis (CAUSAL/STATS, `data/scripts/cm7_analyze.py`).** ATE = **-0.0386**;
  exact 2-phase randomization p = **0.0733** (20-subset robustness p = 0.0754); list-level
  bootstrap 95% CI [-0.079, 0.002]; subject-level (nesting-aware) CI [-0.087, 0.011].
  **counterfactual_status = experimentally_identified** (CM-6 engine + RandomizedEvidence).
  Corroborating list-level contrast -0.0080 (p=0.712); latency null (p=0.163); semantic CTE
  0.046 (MiniLM centroid, negligible vs mean-pairwise 0.981).
- **Data quirks handled.** 14/26 sessions truncated (555 lists; within-list ATE unbiased);
  repeated recall attempts (match-any integrity); resp_word NaN vs `<>` encoding; the
  serial-position confound is canceled by the balanced alternating phase (start-on=109,
  start-off=107; decomposition: stimulation delta ~ -0.038, position (odd-even) ~ -0.044,
  imbalance term -0.0004).
- **Destructive controls (all ~0).** NC1 X-within-list perm null mean 0.0000; NC2 Y-perm
  0.0005; NC4 no-intervention (fake X on ret-stim lists) 0.0016. The machinery does not
  hallucinate an effect. Integrity 3328/3330 (99.94%); 0 missing official outcomes; 2
  unmatched pairs documented (both official_correct=0).
- **Red-team (REVIEWER): GO-WITH-CHANGES.** Leakage PASS (no post-treatment variable in the
  adjustment set; retrieval-stim excluded; list/subject-level inference). Overclaiming PASS
  (site-specific wording respected; no "enhances memory"/free-will/oracle). All 4 changes
  applied: (1) permutation-null CI + labeled list/subject CIs; (2) decision-mapping bug
  fixed (failed controls -> BLOCK, not PARTIAL); (3) Y<0 count + mismatched-pair
  documentation; (4) "small negative effect not excluded" caveat.
- **Decision: CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT** (claim C-010, L6). The METHOD is
  validated (leakage PASS, destructive controls ~0, correct inference, correct engine
  labeling); the specific causal effect is a valid null (small, non-significant reduction
  in recall; a small negative effect to ~-0.079 is not excluded).
- **Next.** CM-8 (Pre-Oracle / Break-the-Chain own experiment, IRB-gated) — the first own
  experiment (E8 voluntary redirection), NOT THE ORACLE.

## 2026-09-17 — CM-8: Pre-Oracle / Break-the-Chain — staged, data-independent gates passed

- **Goal.** The first own experiment, engineered around causal redirection of a PREDICTED
  semantic trajectory: can a deliberate (GENERAL REDIRECT) or externally-induced (SPECIFIC
  CUE) intervention causally redirect the trajectory? North-star, NOT THE ORACLE (the
  participant is not shown the exact prediction).
- **Transition.** CM-2/3 `history -> future`; CM-6 observational structure can't establish
  causality; CM-7 validated the causal machinery on public data (null effect); CM-8 designs
  the experiment where intervention + outcome are engineered around redirection.
- **Design (CM-8A).** Within-subject randomized 4-condition: CONTROL / SHAM (matched
  attention, no redirection) / GENERAL REDIRECT (endogenous) / SPECIFIC CUE (exogenous).
  Primary = BRP; ATE_GENERAL and ATE_CUE estimated separately vs pooled CONTROL/SHAM
  (SHAM-alone sensitivity); subject-clustered permutation test; N=20 (24 trials).
- **BRP/basin (CM-8B).** Predicted-future basin = ball around the frozen forecast, radius =
  held-out 90th-pct prediction-error norm (prospective, not tuned to outcomes);
  `src/causal_mind/causal/predicted_basin.py` (extends the CM-6 SemanticBasin).
- **Estimator validation (CM-8D, G2 PASS).** `data/scripts/cm8_synthetic.py`: H0 type-I
  error 0.113 (≈α=0.10); known effects recovered (bias < 0.007 at push 0.3/0.6/1.0).
- **Power (CM-8E, G4 PASS).** `data/scripts/cm8_power.py`: ICC 0.2, N=20 → 80% power for a
  BRP difference ≈ 0.11 (α=0.05); larger effects need fewer subjects.
- **Platform (CM-8C).** `docs/cm8_realtime_platform.md`: capture -> ThoughtState -> frozen
  predictor -> basin -> randomization -> intervention renderer -> post-capture -> outcome
  engine; auditable timestamps; outcome engine reuses the CM-6/CM-8B machinery.
- **Prereg + SAP (CM-8F) + Ethics (CM-8G).** `docs/cm8_preregistration.md` (frozen primary
  endpoint, exploratory secondaries, pre-specified exclusions, decision rules);
  `docs/cm8_ethics.md` (minimal risk; privacy-by-design for sensitive thought streams;
  consent/debrief/data-mgmt drafts).
- **Literature audit.** `docs/research/cm8_literature_audit.md`: thought suppression /
  ironic rebound, cognitive control, CBM/ABT, sham/demand best practices, capture-modality
  reactivity, planning effect sizes, and the novelty gap.
- **Red-team (G7).** Self GO-WITH-CHANGES (5 fixes: reference-arm rigor, semantic cue-echo
  guard, fatigue, horizon-fishing, calibration modality) + independent REVIEWER confirmatory
  pass GO-WITH-CHANGES (primary estimands clean — no leakage, valid inference, ungameable
  basin; the endogenous-vs-exogenous contrast and the CUE priming confound are disclosed as
  secondary/exploratory). `docs/review/cm8_redteam.md`.
- **Status: `CM8_READY_FOR_ETHICS_SUBMISSION`.** All data-independent gates (G1–G8)
  satisfied at the design level. The only blocker to human data is ethics/IRB approval +
  the pilot (CM-8P, gated) before the confirmatory run (CM-8H, gated). Oracle (CM-9)
  remains gated. No free-will claim.
