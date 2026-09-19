# CM-8 — Pre-Oracle / "Break the Chain" — Task DAG

- **North-star question:** Can a deliberate or externally-induced intervention
  **causally redirect a predicted cognitive (semantic) trajectory**?
- **Position in the genealogy:**
  - CM-2/3: `history -> future` (prediction).
  - CM-6: observational structure cannot establish causality.
  - CM-7: causal intervention machinery validated on a public randomized dataset
    (ds005494) — primary effect null, but the method is validated.
  - **CM-8: the first own experiment, engineered around trajectory redirection.**
- **Not THE ORACLE.** CM-8 is PRE-ORACLE: the participant is NOT shown the model's
  exact next-thought prediction. Oracle (CM-9) stays gated.

## Phases and dependencies

```
LIT (literature audit)
  |
  +--> CM-8A (formal experimental design: conditions, sham, randomization, timeline)
  |        |
  |        +--> CM-8F (preregistration + SAP)
  |        +--> CM-8G (ethics/IRB package)
  |
  +--> CM-8B (formalize BRP + semantic basin; calibrate on historical/synthetic data)
           |
           +--> CM-8D (synthetic participant simulator + validate estimators on
           |          known effects/nulls)
           |        |
           |        +--> CM-8E (power analysis via simulation)
           |        |        |
           |        |        +--> CM-8F, CM-8G (N + burden)
           |        |
           |        +--> CM-8H (confirmatory; gated by pilot + approval)
           |
           +--> CM-8C (realtime prediction + intervention platform)
                    |
                    +--> CM-8P (human pilot; gated by ethics approval)
                             |
                             +--> CM-8H
```

- **LIT** = literature audit (voluntary thought redirection / suppression / cognitive
  control). Informs CM-8A (sham, modality) and CM-8B (BRP/basin), and seeds CM-8E
  (plausible effect sizes).
- **CM-8A** = formal experimental design (the 4 conditions, sham spec, randomization
  scheme + seed, trial timeline, capture modality).
- **CM-8B** = formalize BRP + the predicted-future semantic basin (prospective geometric
  rule, calibrated on held-out historical trajectories; NOT tuned to outcomes).
- **CM-8C** = realtime platform (thought capture -> ThoughtState -> frozen predictor ->
  basin -> randomization -> intervention renderer -> post-capture -> outcome engine),
  high-resolution auditable timestamps.
- **CM-8D** = synthetic participant simulator (generates thought streams with KNOWN
  intervention effects and nulls) + validate the causal estimators recover the known
  effects and return null under H0.
- **CM-8E** = power analysis via simulation (participants x trials, within-subject
  correlation, baseline BRP, minimally interesting effect, condition count, attrition).
- **CM-8F** = preregistration + statistical analysis plan (frozen primary endpoint).
- **CM-8G** = ethics/IRB package (consent, privacy, risk, data management, debrief).
- **CM-8P** = human pilot (gated by ethics approval).
- **CM-8H** = confirmatory experiment (gated by pilot + approval).

## Data-independent gates (must all pass autonomously before human data)

| gate | name | pass criterion |
| --- | --- | --- |
| G1 | BRP/basin frozen | BRP + predicted-future basin defined prospectively, calibrated on held-out data, one basin metric frozen |
| G2 | estimator validation | synthetic simulator: known ATE recovered (CI covers truth), H0 -> null (no false positive) |
| G3 | randomization frozen | scheme + seed + manifest frozen; counterbalanced; no long same-condition runs |
| G4 | power | N + trials/participant from simulation; power curves; not a guess |
| G5 | prereg + SAP | primary endpoint, secondary outcomes, analysis plan, exclusions frozen |
| G6 | ethics package | consent, privacy, risk, data mgmt, debrief drafted |
| G7 | red-team GO | demand/sham/cue-repetition/leakage/horizon-fishing all addressed |
| G8 | model freeze | the CM-3-style predictor used to define the predicted basin is frozen (no retraining on confirmatory outcomes) |

## Success states

- Before human data: `CM8_READY_FOR_ETHICS_SUBMISSION`.
- After pilot: `CM8_PILOT_PASS` / `CM8_PILOT_ITERATE`.
- After confirmatory: `CM8_PASS_CAUSAL_TRAJECTORY_REDIRECTION` /
  `CM8_PASS_EXOGENOUS_ONLY` / `CM8_NULL_NO_REDIRECTION` / `CM8_BLOCK`.

## Claim boundary (even on a PASS)

Do NOT claim "free will exists." The justified ceiling is:
> Deliberate cognitive-control instructions (or an external semantic cue) causally alter
> the distribution of subsequent thought trajectories under the tested experimental
> conditions.

## Oracle gate (CM-9 remains gated until CM-8 establishes)

1. reliable online prediction; 2. reliable basin metric; 3. experimentally-identified
redirection; 4. persistence beyond immediate lexical response; 5. test-retest reliability;
6. acceptable participant burden.
