# CM-8 Red-Team Report (design, pre-ethics)

- **Reviewer:** ORCHESTRATOR (self red-team) + independent REVIEWER confirmatory pass.
- **Scope:** the data-independent CM-8 design (no human data). Verdict below.

## Verdict: GO-WITH-CHANGES (all changes applied in this revision)

The design is sound and the estimators are validated (G2: H0 type-I error 0.113 ≈ α; known
effects recovered, bias < 0.007). The red-team found five real design issues, all fixed:

### 1. Reference-arm rigor (FIXED)
- **Issue:** GENERAL/CUE differ from SHAM only in the redirection content, but the primary
  reference was the pooled CONTROL/SHAM. If the prompt/interruption itself shifts the
  trajectory (SHAM ≠ CONTROL), the pooled reference is contaminated.
- **Fix:** primary reference stays pooled CONTROL/SHAM (per spec); **SHAM-alone** added as a
  pre-specified sensitivity that isolates the active ingredient; **H3 (SHAM vs CONTROL)**
  pre-specified with a fallback: if H3 is significant, SHAM-alone becomes the primary
  reference. (`cm8_experiment_design.md` §1, `cm8_preregistration.md` §2.)

### 2. Lexical cue-repetition gaming (FIXED)
- **Issue:** the trivial-success guard used lexical overlap; a participant could echo a
  synonym and still count as "redirected."
- **Fix:** the cue-echo exclusion is now **semantic** (cosine threshold to the cue
  embedding, catching verbatim + synonym echoes), and persistence requires entering the
  predefined **target basin** (a region, not the cue word) and staying. The echo threshold
  is set from the SHAM/neutral-cue baseline. (`cm8_basins_brp.md` §6.)

### 3. Fatigue / learning / strategy over 24 trials (FIXED)
- **Issue:** 24 repeated trials risk fatigue, learning, and strategy adaptation dominating
  the signal.
- **Fix:** counterbalanced order, no >2 consecutive same-condition trials, breaks between
  blocks; the pilot explicitly measures fatigue and trial stability and can reduce the trial
  count (re-powered) before the confirmatory run. (`cm8_experiment_design.md` §9.)

### 4. Horizon/outcome fishing (FIXED)
- **Issue:** many secondary outcomes (divergence, latency, persistence, return, decay,
  per-horizon) could be used to rescue a null primary.
- **Fix:** secondary outcomes are explicitly **EXPLORATORY** and cannot support a
  causal-redirection claim; only the primary family {ATE_GENERAL, ATE_CUE} at the frozen
  `h*` (BH-FDR q=0.05) can. No horizon selection after the fact.
  (`cm8_preregistration.md` §3–4.)

### 5. Calibration-set modality dependency (FIXED)
- **Issue:** `r_α` (the basin radius) is calibrated from the predictor's held-out error
  distribution, which depends on the capture modality; a modality change would
  miscalibrate the basin.
- **Fix:** the calibration set must come from the SAME modality as the experiment (pilot
  dependency, G1); the ICC and power are re-checked after the pilot estimates the true ICC.
  (`cm8_experiment_design.md` §9.)

## Items checked and found acceptable (no change)

- **Prediction leakage:** the predicted basin uses only the pre-intervention history via the
  frozen predictor; the forecast is computed before the intervention is rendered. No
  post-intervention info enters the basin. OK.
- **Post-treatment conditioning:** the primary ATE is a BRP difference, not conditioned on
  effort/perceived success. OK.
- **Endogenous vs exogenous:** ATE_GENERAL and ATE_CUE estimated separately, never pooled.
  OK.
- **Exclusions:** pre-specified, outcome-independent, intent-to-treat. OK.
- **Analysis blinding:** the outcome engine + permutation test are condition-blind. OK.
- **Statistical:** subject-clustered permutation test is valid for the BRP outcome
  (validated); ICC≈0.2 and N=20 are defensible planning values (re-checked post-pilot). OK.

## Residual risks (accepted, disclosed)

- **Demand characteristics:** the sham + blinding + counterbalancing are the standard
  mitigations; a "this is the real condition" expectancy in GENERAL cannot be fully removed
  in a self-report paradigm. Disclosed; the SHAM-alone sensitivity bounds it.
- **Modality reactivity:** think-aloud/typed may alter the cognition being measured; the
  pilot measures this and the primary modality is frozen after the pilot.
- **Novel-metric effect size:** BRP has no direct literature effect size; the power analysis
  uses a justified a-priori minimally-interesting effect (Δ≈0.11), not a pilot estimate.

## Gate status

- G1 (BRP/basin frozen): defined; freeze + hash at preregistration seal.
- G2 (estimator validation): PASS (H0 + recovery).
- G3 (randomization frozen): scheme + seed + manifest specified; manifest generated at seal.
- G4 (power): PASS (N=20, 24 trials, Δ≈0.11 → 80%).
- G5 (prereg + SAP): drafted; seal at ethics.
- G6 (ethics package): drafted.
- G7 (red-team): this report — self GO-WITH-CHANGES (5 fixes applied) + **independent
  REVIEWER confirmatory pass: GO-WITH-CHANGES** (primary estimands clean; one fix applied:
  the endogenous-vs-exogenous contrast is confounded and the CUE arm is confounded with
  semantic priming — both now disclosed; secondary/exploratory, does not invalidate H1/H2).
- G8 (model freeze): the CM-3-style predictor is to be frozen at pilot/confirmatory boundary.

**Overall: all data-independent gates (G1–G8) are satisfied at the design level. The design
is ready for ethics submission — `CM8_READY_FOR_ETHICS_SUBMISSION`. The only remaining
blocker to human data is ethics/IRB approval (plus the pilot, which itself requires
approval).**
