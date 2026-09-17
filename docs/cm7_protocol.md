# CM-7 — Frozen Protocol: Public Intervention Method Validation (ds005494)

- **Status:** FROZEN / SEALED — finalized before any decisive outcome estimate is computed.
- **Date:** 2026-09-17 · **Author:** ORCHESTRATOR (CM-7)
- **Companions:** `docs/datasets/ds005494_audit.md` (audit), `docs/cm7_identification.md`
  (identification, A1–A5), `src/causal_mind/causal/counterfactuals.py` (engine),
  `src/causal_mind/causal/metrics.py` (CTE/BRP).
- **Scope:** validate that the CAUSAL MIND intervention framework correctly recovers an
  experimentally-identified causal effect `P(Y_future | do(X))` in an independent public
  dataset. This is a **method-validation** exercise. It is NOT a claim about "hippocampal
  stimulation enhances memory" in general, and NOT a claim about spontaneous thought
  redirection or free will.

---

## 1. Data

- **Dataset:** OpenNeuro ds005494, v1.0.1 (Herrema & Kahana, CC0). N=20 subjects, 26 sessions.
- **Acquired (minimal, no iEEG):** per-session `beh.tsv` (26/26), `participants.tsv`,
  `wordpool_EN.txt`, `dataset_description.json`, per-session `electrodes.tsv` / channel
  sidecars (for the optional neural stage). Raw under `data/raw/ds005494/`.
- **Manifest:** `data/manifests/ds005494_manifest.json` (files, SHA-256, row counts,
  acquisition timestamp).

## 2. Eligible units

- **Lists:** `list` field 1–25 within each session. The practice list (`list = -1`) is
  EXCLUDED.
- **List type** (derived per list, mutually exclusive — no list has both):
  - `enc-stim`: has ≥1 `STUDY_PAIR` row with `stimulation = 1` (stimulation at encoding).
  - `ret-stim`: has ≥1 `STIM_ON` row co-occurring with the recall phase (`TEST_PROBE` /
    `REC_START`) and NO `STUDY_PAIR` row with `stimulation = 1`.
  - `no-stim`: `stim_list = 0` for all rows (no stimulation).
- **Primary population:** all pairs in `enc-stim` lists (across all 26 sessions / 20 subjects).
- **Expected counts (to be verified by the parser, not assumed):** 260 enc-stim lists,
  260 ret-stim lists, 130 no-stim lists; within each enc-stim list exactly 3 pairs with
  `X=1` and 3 with `X=0`. If any enc-stim list does not have exactly 3/3, it is flagged and
  the deviation reported (a 3/3 violation would indicate a parsing or design anomaly).

## 3. Treatment (X)

- **Pair-level (primary):** `X = stimulation` field on the pair's `STUDY_PAIR` row
  (1 = the pair's encoding presentation received the documented train; 0 = not).
- **List-level (corroborating):** `x = 1` for enc-stim lists, `x = 0` for no-stim lists.
- `X` is a fixed, logged train (anode/cathode, amplitude, 50 Hz, 230 pulses, 300 µs, 4.6 s,
  onset −200 ms) — single version within a subject (consistency holds within subject).

## 4. Outcome (Y)

- **Primary:** `Y = correct` (0/1) on the `STUDY_PAIR` row (pre-labeled pair outcome; the
  parser MUST re-verify this against the corresponding `REC_EVENT` row for all 26 sessions
  before any result is reported — a data-integrity gate).
- **Secondary:**
  - `response_time` (s) — from the matching `REC_EVENT` row (join on `list` + `serialpos`);
    latency within the 5 s recall window, defined for all responses.
  - `resp_word` — the recalled word on the `STUDY_PAIR` row (`n/a` = no word vocalized).
    Three-level outcome: correct word / wrong word / no word.

## 5. Estimands

1. **Primary — site-specific ATE (pair-level, within enc-stim lists):**
   `ATE = mean over enc-stim lists l of [ mean(Y | X=1, l) − mean(Y | X=0, l) ]`.
   The within-list contrast differenced-out list-level confounds; the estimand is the
   contextual effect of stimulating a pair's encoding given the enc-stim list context
   (identification §1.3).
2. **Corroborating — list-level contrast:** mean recall of enc-stim lists (260) vs no-stim
   lists (130). A different estimand (includes spillover onto the 3 non-stim pairs);
   reported as corroboration, not the primary.
3. **Distributional effect:** the full shift in the recall distribution under do(X=1) vs
   do(X=0): (a) the binary core = ATE; (b) the latency distribution (among all responses);
   (c) the recalled-word identity distribution (semantic CTE, §7).
4. **CTE (causal trajectory effect):** `causal_trajectory_effect(future_stim, future_nostim)`
   where the "future state" is the recall outcome vector (§7). The randomization is the
   control; no matched-control calibration is applied (the matched-control sampler is for
   observational baselines and is NOT applicable to a randomized contrast).
5. **BRP:** NOT computed as a primary metric — cued recall has no free semantic basin, so
   `branch_redirection_probability` is not meaningful here. Recorded as "not applicable"
   with justification (identification §1.5 note).

## 6. Analysis plan (primary)

- **Unit of inference:** the enc-stim list (260). Pairs are nested in lists; lists in
  sessions; sessions in subjects (20). Trial-level n is NOT the effective n (A3).
- **Point estimate:** the primary ATE of §5.1 (within-list contrast, averaged over lists).
- **Uncertainty (primary):** **randomization (permutation) inference.** Permute the `X`
  labels WITHIN each enc-stim list (re-choose which 3 of 6 positions are X=1, uniformly),
  recompute the within-list ATE, repeat B=20000 times. Two-sided p-value =
  `mean(|ATE_perm| ≥ |ATE_obs|)`. 95% CI from the 2.5/97.5 percentiles of the permutation
  null (or a list-level bootstrap of the within-list contrasts; report both, permutation
  primary).
- **Sensitivity (subject-level):** average each subject's within-list contrasts, then
  aggregate over the 20 subjects (subject-level permutation / CI). Guards against
  between-subject heterogeneity making the list-level CI anti-conservative.
- **Covariates:** none required for validity (randomization). Optional precision
  covariates (serial position, list position for carryover) are run ONLY as sensitivity
  analyses and never alter the primary estimand.
- **Corroborating list-level test:** permutation of the enc-stim/no-stim list-type label
  within each subject (preserving the per-subject 10/5 ratio), B=20000, on list-mean recall.

## 7. Distributional / CTE construction

- **Semantic future state:** embed each pair's `resp_word` with the frozen MiniLM
  (`sentence-transformers`, `HF_HOME=/home/jovyan/work/.hf-home`). `n/a` (no word) is a
  distinct category, represented by a fixed "no-response" vector (the MiniLM embedding of
  the literal string `"<no response>"`), NOT dropped. The recalled-word cloud under do(X=1)
  vs do(X=0) is compared with `causal_trajectory_effect` (centroid distance) and the
  full pairwise distance.
- **Latency distribution:** compare `response_time` (stim vs no-stim) with a permutation
  test (permute the X label within list on the latency outcome) and report mean/median
  difference.
- **Word-identity shift:** report the change in the correct / wrong-word / no-word
  proportions under do(X=1) vs do(X=0) (a 3-way distributional contrast).

## 8. Destructive / placebo controls (NC1–NC6) — the machinery must pass all

These confirm the estimated effect is produced by the actual randomized assignment, not a
pipeline artifact. Each must yield an effect indistinguishable from 0 (p > 0.10, |ATE|
within the central 95% of its own permutation null):

- **NC1 — within-list X permutation (the primary null):** permute X within each enc-stim
  list. This is the reference distribution for the primary test; the observed ATE must sit
  in its tail to be significant. (If the "effect" survives X permutation, the pipeline is
  broken.)
- **NC2 — outcome permutation:** permute `Y` (correct) across all pairs in enc-stim lists.
  Expect ATE → 0.
- **NC3 — cross-subject X:** assign each list's X-pattern from a different subject's
  session (break the within-subject treatment consistency). Expect ATE → 0.
- **NC4 — retrieval-stim mislabeled as encoding:** take ret-stim lists (which had NO
  encoding stimulation) and assign them a fake X-pattern; compute the "encoding ATE."
  Expect → 0 (there was no encoding intervention to detect).
- **NC5 — enc-vs-ret non-contrast:** compare enc-stim list recall vs ret-stim list recall.
  Both are stimulated (different timing); this is NOT the randomized encoding contrast.
  Reported to show it is not interpretable as the encoding ATE (expect ~0 or explicitly
  non-causal).
- **NC6 — position/phase placebo:** stratify the primary ATE by serial position (1–6) and
  by phase (start-on vs start-off). The effect must not be driven by a single position
  (e.g., only position 1 or 6) — otherwise it is a position artifact, not a stimulation
  effect. Report the per-position ATEs.

## 9. Counterfactual engine labeling

- The primary result is emitted via
  `IdentifiedCounterfactual(estimand).from_experiment(ATE, RandomizedEvidence(...),
  justification, audit)` → `counterfactual_status = "experimentally_identified"`.
- `RandomizedEvidence(experiment_id="ds005494-enc-stim", randomized=True,
  n=<260 enc-stim lists, stated as the unit>, effect_estimate=ATE, ci_low, ci_high,
  notes="randomization unit=list; scheme 10/10/5 + phase 50/50; source=dataset README +
  audit; identification A1–A5 (docs/cm7_identification.md)").
- The engine's refusal semantics are a HARD gate: if `RandomizedEvidence` is invalid the
  result cannot be labeled causal and the analysis stops.
- All destructive-control results are emitted as `observational_only` (they are null
  references, not causal claims).

## 10. Exclusions & leakage guards (frozen)

- **Excluded from adjustment (post-treatment / mediators, identification §7):** all iEEG
  signals, arousal/attention state, seizure activity, subjective state/expectation, and
  math-distractor performance. None enter any model.
- **Pre-treatment covariates only** (serial position, list position, word difficulty) may
  appear, and only in sensitivity analyses.
- **Leakage gate (before any result is reported as validated):** reviewer audit that (a) no
  post-treatment variable enters adjustment, (b) the pre-labeled `Y` is re-verified against
  `REC_EVENT` across all 26 sessions, (c) inference clusters at the list/subject level (A3),
  (d) the retrieval-stim contrast is not reported as an encoding/future-state effect.

## 11. Success criteria & decision mapping

- **CM7_PASS_PUBLIC_INTERVENTION_VALIDATION:** the primary ATE is a real, identifiable
  causal effect (permutation p < 0.05, CI excludes 0), the counterfactual engine labels it
  `experimentally_identified`, AND all NC1–NC6 destructive controls pass (effect vanishes
  under shuffles). The framework recovered a genuine `P(Y_future | do(X))`.
- **CM7_PARTIAL_METHOD_VALIDATION:** the machinery is validated (NC1–NC6 pass, randomization
  inference correct, engine labels correctly) but the primary ATE is not statistically
  significant (null or underpowered). The method works; no positive causal effect recovered.
- **CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT:** a valid null — the framework correctly shows no
  recoverable causal effect (destructive controls pass, primary CI includes 0, and the null
  is not an artifact).
- **CM7_DATASET_NOT_CAUSALLY_IDENTIFIABLE:** the identification audit (A1–A5) fails on the
  actual data (e.g., randomization not verifiable, differential missingness of Y by X,
  3/3 structure violated) → STOP, no causal claim.
- **CM7_BLOCK:** a leakage/validity gate fails (post-treatment leakage, integrity gate
  fails, engine refusal) → STOP.

A null is a valid outcome. The estimand is NOT weakened to force a PASS.

## 12. Claims boundary (even on PASS)

Permitted: "the CAUSAL MIND intervention framework recovered and validated an
experimentally-identified causal effect — the site-specific effect of open-loop stimulation
of the targeted hippocampal/entorhinal electrode at encoding on subsequent cued recall — in
the independent public dataset ds005494."

NOT permitted: "hippocampal stimulation enhances memory" (site-specific, train-specific,
population-limited); "causal redirection of spontaneous thought"; "free will"; "THE ORACLE
validated"; general mental causation. Claim level: L6 (causal evidence from valid
intervention/identification), raisable only by a reviewer gate pass.

## 13. Freeze statement

This protocol is sealed. The decisive primary ATE, its CI/p-value, and the distributional
/CTE estimates will be computed ONCE after this document is committed. No estimand,
covariate, or control will be added or changed after the first decisive run except by a
documented, pre-justified amendment that does not depend on the observed outcome.
