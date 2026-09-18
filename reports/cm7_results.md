# CM-7 — Public Intervention Method Validation (ds005494) — Results

- Generated: ds005494 vv1.0.1, N=20 subjects, 26 sessions.
- **Decision: `CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT`** (integrity_ok=True, nc_all_pass=True)

## Integrity gates
- STUDY_PAIR official outcome matches a REC_EVENT attempt: 3328/3330 (0.999)
- pairs with missing official correct (Y<0): 0
- official outcome matching NO recall attempt: 2 -> ['sub-R1060M/ses-0/list3/pos1 (BREAD-GLASS) official_correct=0', 'sub-R1162N/ses-0/list13/pos4 (WEED-GRASS) official_correct=0']
- enc-stim lists not 3/3: 0
- sessions with <25 completed lists (truncated): 14/26; total lists = 555 (recording ended early in some sessions)

## Counts
- lists: enc-stim=216, ret-stim=226, no-stim=113
- enc-stim pairs: X=1 648, X=0 648

## Primary ATE (site-specific, encoding stimulation -> cued recall)
- ATE = **-0.0386**
  - exact 2-phase randomization p = 0.0733 (20-subset robustness p = 0.0754)
  - list-level bootstrap 95% CI = [-0.0787, 0.0015] (lists as independent; mildly anti-conservative)
  - permutation-null 95% interval = [-0.0417, 0.0387] (central 95% of the randomization null)
- n enc-stim lists = 216, n subjects = 20
- subject-level (nesting-aware) sensitivity: ATE = -0.0344, 95% CI [-0.0874, 0.0114]
- counterfactual_status = **experimentally_identified** (is_causal_claim=True)
- NOTE: the CI upper bound (0.002) rules out positive effects, but a small NEGATIVE effect down to -0.079 is NOT excluded (stimulation may slightly reduce recall).
- position robustness: phase balanced (start-on=109, start-off=107, balanced=True); decomposition: stimulation effect delta = -0.0382, serial-position effect (odd-even) = -0.0444. The balanced phase cancels the position confound, so the ATE = the stimulation effect.

## Corroborating list-level contrast
- enc-stim list mean = 0.3696, no-stim list mean = 0.3776, diff = -0.0080 (perm p = 0.7120)

## Distributional effect
- latency: stim 2.764s vs no-stim 2.668s (diff 0.097s, perm p = 0.1625)
- word identity stim: correct=0.350 wrong=0.168 noword=0.481
- word identity nostim: correct=0.389 wrong=0.162 noword=0.449
- semantic CTE (MiniLM centroid distance, stim vs no-stim recall): 0.0462 (mean pairwise 0.9812)

## Destructive / placebo controls (must all be ~0)
- NC1 X-perm null mean = 0.0000 (sd 0.0209); observed ATE = -0.0386 (exact 2-phase p 0.0733)
- NC2 Y-perm: mean 0.0005 (95% -0.0509, 0.0509)
- NC3 position-only confound (odd vs even, ignoring stim): -0.0448 (serial-position effect; canceled by balanced phase randomization)
- NC4 no-intervention (ret random-X): mean 0.0016 (95% -0.0676, 0.0725)
- NC5 enc-vs-ret (informational): diff = 0.0127
- NC6 per-position ATE: {'1': -0.07210837691846006, '2': -0.039012260996313164, '3': -0.033524822086941575, '4': -0.057532367315442035, '5': -0.015519163165566285, '6': -0.011317842750578788}
- NC6 phase: start-on(1,3,5)=-0.08256880733944955, start-off(2,4,6)=0.006230529595015571
