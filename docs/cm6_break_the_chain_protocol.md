# CM-6 — Break-the-Chain Protocol (Target Selection + First Intervention Design)

Generated: 2026-09-16 · Engine: ORCHESTRATOR (CM-6C / CM-6F / CM-6G / CM-6H).
Inputs: `docs/cm6_candidate_causal_graph.md` (CM-6A), `docs/datasets/cm6_intervention_dataset_audit.md`
(CM-6B), `src/causal_mind/causal/` (CM-6D/E metrics + counterfactual engine).

> **North-star.** Which elements of preceding cognitive history actually **change** the
> distribution of future thought when intervened upon? The single highest-priority question
> this document answers: **what is the cleanest experiment that distinguishes "X predicts
> future thought" from "changing X changes future thought"?**

## 0. The prediction-vs-causation test, operationalized

A clean causal test has three parts, and the **cleanest** experiment is the one that
measures all three in the *same participants, with a randomized intervention*:

1. **The predictable baseline** — `P(T_future | history)`: what the frozen CM-3 model
   predicts the next thought will be (the "X predicts" side).
2. **The randomized intervention** — `do(X)`: a manipulation assigned independently of the
   participant's latent state (the "changing X" side).
3. **The calibrated divergence** — the *difference* between the actual post-intervention
   trajectory and the predicted baseline, measured by the CM-6D metrics (BRP, CTE,
   trajectory divergence) **relative to matched control transitions** (so generic drift is
   not read as an effect).

The causal effect is `effect = metric(intervened) − metric(matched control)`. If it is
~0, the intervention did nothing (prediction held). If it is >0 and stable, changing X
changed the future. **This contrast is the entire game.**

---

## 1. CM-6C — Causal target ranking

Ranked by **expected scientific information gain** for the north-star, weighting: (1)
observational support (CM-6A), (2) plausibility of a clean randomized intervention, (3)
availability of a public randomized dataset (CM-6B), (4) whether the outcome is a *future
free cognitive/semantic state*, (5) whether it is representable in the ThoughtState space.

| Rank | X (edge) | Candidate effect | Obs. evidence (CM-6A) | Identifiability | Public dataset (CM-6B) | Expected info gain |
| --- | --- | --- | --- | --- | --- | --- |
| **1** | **E8 — voluntary redirection** (CM-6H) | a redirection *instruction* changes the next thought's semantic basin | none (the gap — no observational handle) | identifiable **only** by our randomized experiment | **none public** | **HIGHEST** — directly operationalizes prediction-vs-causation; prerequisite to THE ORACLE |
| **2** | **E1 — affect** (emotional framing / induction) | inducing an emotion shifts subsequent free thought | **weak within-subject** (R² 0.01–0.05; pooled 0.20 is a GPT-rating-baseline artifact, CM-6J); literature-motivated | NOT identifiable observationally (baseline-mood + GPT-baseline confound); identifiable if randomized | ds006583 (music→*affect* only, N=43) | **MEDIUM-HIGH** — mature paradigm, but observational support is weak; needs own experiment for a *free-thought* outcome |
| **3** | **E3 — memory cue** (cued recall) | a cue steers the recalled/produced associate | conceptual (memory lit.) | **IDENTIFIABLE in ds005494** (randomized open-loop stim + cue → vocal recall) | **ds005494** (N=20, iEEG, randomized) | **MEDIUM-HIGH** — only public `do(X)→future semantic state`; validates the *method* |
| 4 | E2 — semantic prime | a prime shifts the next thought's content | conceptual | identifiable if randomized | EEG priming (RT/ERP outcomes, not free thought) | MEDIUM |
| 5 | E4 — goal / task-set | a goal instruction shifts verbal content | conceptual | identifiable if randomized | ds006240 (language switch→speech, N unconf.) | MEDIUM |
| 6 | E5 — attentional cue | a cue shifts attention→thought | conceptual | partial | Posner (RT outcomes) | LOW-MEDIUM |
| 7 | E6 — expectation / prior | a prior shifts the prediction | conceptual | partial | — | LOW-MEDIUM |
| 8 | E7 — thought suppression | suppression changes intrusion | conceptual | partial | white-bear (no public thought-report outcome) | LOW |

### The choice (first causal edge to test)

We do **not** test everything at once. Two complementary first steps:

- **Step 1 — validate the method on public data (no new data, low risk):** run the CM-6
  intervention-analysis pipeline (CM-6D metrics + matched controls + the counterfactual
  engine at `experimentally_identified` status) on **ds005494** (E3). It is the only public
  dataset with a *genuinely randomized* `do(X)` followed by a *measured future semantic
  state*. This proves we can measure `P(T_future | do(X))` correctly before we spend
  participants. *Accept the caveats:* iEEG clinical cohort, retrieved (not free) semantic
  state, N=20, and the primary X is neural stimulation.
- **Step 2 — the first OWN experiment (the real causal edge):** the **CM-6H pre-Oracle
  experiment** (below), which tests **E8 (voluntary redirection)** at its simplest form. It
  is the cleanest single experiment that (a) measures the predictable baseline in the same
  participants, (b) randomizes the intervention, (c) measures a pre-registered basin-departure
  outcome, and (d) is the required precursor to THE ORACLE.

**Why E8 (redirection) before E1 (affect) for the first own experiment:** E1 is the
strongest *literature-motivated* cognitive edge, but its ds006067 *observational* support is
**weak after the GPT-rating-baseline correction** (within-subject R² 0.01–0.05; the pooled
0.20 is an artifact — see `cm6_candidate_causal_graph.md` §5.1/§7). The pre-Oracle
redirection experiment (E8) has the *cleanest within-subject baseline + randomized
intervention + cleanest outcome*, and it is on the critical path to THE ORACLE (the
project's north-star). E1 (affect → free thought) is the strongest *parallel/next*
own-experiment candidate and is explicitly queued after the redirection method is validated.

---

## 2. CM-6H — Pre-Oracle experiment (FIRST own experiment)

**Question.** Can a participant deliberately leave a predicted semantic basin **without**
being shown the exact predicted future? (Estimates *baseline voluntary trajectory control*
before adding recursive prediction.)

**Hypothesis (falsifiable).** A randomized redirection instruction increases the
probability that the next thought leaves the predicted baseline basin (BRP), above matched
control transitions; the effect is larger for a SPECIFIC CUE than for a GENERAL REDIRECT
instruction, and both are above CONTROL.

### Design

- **Participants:** N≥24 (pilot; power analysis in §5). Healthy adults, think-aloud
  (speak continuously), as in ds006067.
- **Thought segmentation:** same pipeline as ds006067 (thought events with onset/duration/
  transcript → frozen MiniLM embedding).
- **Per-trial procedure:**
  1. **Observe (Phase A):** collect a history window (k≈3 recent thoughts) → current basin.
  2. **Predict (Phase B):** the frozen CM-3 multi-horizon model predicts the near-future
     basin `T[t+h]` (h=1 primary). This is the *predictable baseline*.
  3. **Randomize (Phase C):** within-subject, counterbalanced, one of:
     - **CONTROL** — no instruction; participant thinks normally. *(the "X predicts" side)*
     - **SHAM INSTRUCTION** *(CM-6J fix — demand-characteristic control)* — a neutral
       instruction with **no redirection content**, e.g. "Keep thinking about what you've
       been thinking." Separates "receiving *any* instruction / compliance / novelty" from
       the *redirection content* itself.
     - **GENERAL REDIRECT** — "Now think about something different from what you've been
       thinking." *(ENDOGENOUS redirection; no specific target)*
     - **SPECIFIC CUE** — "Now think about **[a semantic CATEGORY different from your
       current topic]**" (prefer a *category*, not a single word, to reduce the verbatim
       shortcut). *(EXOGENOUS redirection; a specific target, chosen off-topic)*
  4. **Measure:** the next thought (and next h thoughts).
- **Primary outcome:** **BRP** = P(next thought leaves the predicted baseline basin |
  condition), using the CM-6D `SemanticBasin` (fitted on the participant's baseline) and
  **calibrated against matched control transitions** (the participant's own CONTROL trials
  + observational matched controls via `sample_matched_controls`).
- **Secondary outcomes:** trajectory divergence (distance from predicted trajectory),
  return-to-baseline probability, intervention effect decay (half-life over h), subjective
  effort, confidence, and the semantic trajectory (embedding path).

### The causal contrast (what it measures)

| Contrast | Mechanism tested |
| --- | --- |
| BRP(GENERAL REDIRECT) − BRP(CONTROL) | **ENDOGENOUS** voluntary control (gross) |
| BRP(GENERAL REDIRECT) − BRP(SHAM) | redirection content, **net of instruction demand** |
| BRP(SPECIFIC CUE) − BRP(CONTROL) | **EXOGENOUS** cue effect (gross) |
| BRP(SPECIFIC CUE) − BRP(SHAM) | cue content, net of instruction demand |
| BRP(SPECIFIC CUE) − BRP(GENERAL REDIRECT) | cue specificity |
| all − matched-control baseline | removes generic drift (the CM-6D calibration) |

CONTROL = "the trajectory was predictable and unfolded as predicted." REDIRECT/CUE =
"changing X changed the trajectory." The *difference* is the causal effect. **This is the
cleanest possible operationalization of prediction-vs-causation.**

### Design fixes (CM-6J red-team, pre-registered before IRB)

1. **Cue-verbatim lexical shortcut (pre-registered rule).** A participant could say the
   SPECIFIC CUE verbatim, leave the predicted basin, and inflate BRP without genuine
   redirection. **Fix:** (a) prefer a semantic *category* over a single word; (b) compute
   BRP on the subset of cue-trial thoughts that do **not** contain the cue string verbatim,
   and report the verbatim-subset BRP separately as a diagnostic; (c) enter cue–thought
   lexical overlap (cosine of cue embedding vs. produced thought) as a **covariate** (not
   "cue identity"). The sham-cue negative control (current-topic cue) stays, but it tests
   "do cues raise BRP at all," not the verbatim shortcut — hence (b) is required.
2. **Per-subject baseline-diversity floor (pre-registered).** A low-diversity participant
   gets a tiny basin and BRP measures triviality, not control. **Fix:** pre-register a
   baseline-diversity floor (e.g., mean pairwise cosine of the participant's baseline
   thoughts, or distinct-topic count) and **report BRP stratified by diversity**; exclude
   only below the floor, with the floor set before data collection.
3. **Counterbalancing scheme (pre-registered).** Specify the order design: a **4×4 Latin
   square** over the four conditions (CONTROL / SHAM / GENERAL REDIRECT / SPECIFIC CUE) in
   blocks, with a **washout** (≥1 neutral thought) between same-condition trials and a
   minimum gap; include **order/block as a covariate**. This controls carryover from a
   REDIRECT into a later CONTROL.
4. **Demand characteristics.** The SHAM INSTRUCTION condition (above) is the primary
   control; additionally, participants are told the study is about "how thoughts change"
   (not "can you redirect your thoughts") to reduce demand.

### What it does NOT test (yet)

It does **not** show the participant the prediction (no REACTIVE condition). REACTIVE
redirection (changing direction *because* one saw the prediction) is the CM-6F break-the-
chain experiment, authorized only after CM-6I (Oracle readiness).

---

## 3. CM-6F — Break-the-Chain experiment (fuller design; gated by CM-6I)

**Question.** Can a predicted thought trajectory be deliberately redirected **when the
participant is shown the prediction?**

### Phases
- **Phase A — Observe:** estimate the participant's baseline trajectory.
- **Phase B — Predict:** predict the near-future cognitive branch (frozen CM-3 model).
- **Phase C — Randomize** one of four conditions:
  - **CONTROL** — no intervention.
  - **CUE** — exogenous semantic redirection (no prediction shown).
  - **VETO** — *show the predicted direction*, instruct the participant to **avoid** it.
  - **REDIRECT** — *show the prediction*, instruct the participant to **choose an
    alternative** semantic branch.
- **Measure:** immediate branch divergence, persistence of divergence, return-to-baseline
  probability, intervention decay, subjective effort, confidence, semantic trajectory.

### CM-6G — three mechanisms as SEPARATE randomized conditions (critical)

| Mechanism | Condition | Definition |
| --- | --- | --- |
| **EXOGENOUS redirection** | CUE | an external cue changes the trajectory |
| **ENDOGENOUS redirection** | (no-prediction redirect instruction) | the participant deliberately changes direction |
| **REACTIVE redirection** | VETO / REDIRECT | the participant changes direction **because they observed a prediction** |

These **must** be separate conditions. Otherwise "agency" (reactive) and "cueing"
(exogenous) are confounded: a participant who changes direction after seeing a prediction
might be reacting to the prediction, merely following a cue, or both. Only the four-way
randomization attributes the effect.

**This is a causal cognitive-control experiment, NOT free-will testing.** We measure
whether a specific, randomized manipulation changes a measurable trajectory metric. We make
no claim to prove or disprove free will.

---

## 4. Analysis plan (pre-registered)

1. **Unit of inference:** the trial (thought), clustered by participant; participant-level
   bootstrap for CIs (subject-level, as in CM-2/3/5).
2. **Primary test:** mixed model `BRP ~ condition + (1|participant)`, with the matched-
   control-calibrated BRP as the outcome; permutation test on the condition effect.
3. **Leakage guards (frozen):** the prediction (Phase B) uses only history strictly before
   the target; the basin is fitted on baseline (pre-intervention) data only; the SPECIFIC
   CUE target is chosen *off-topic* (not the predicted content) to avoid a trivial
   "say the cue" shortcut; cue identity is logged and entered as a covariate.
4. **Negative controls:** (a) a *sham* SPECIFIC CUE drawn from the participant's *current*
   topic (should NOT increase BRP); (b) a *delayed* instruction (after the target thought)
   (should NOT affect it). Both must show ~0 effect.
5. **Multiple comparisons:** the four conditions are the pre-registered family; report all,
   no post-hoc edge fishing.

## 5. Power and ethics

- **Power:** pilot N≥24 to estimate the BRP effect size and variance; a confirmatory N set
  by a post-pilot power analysis on the primary contrast (BRP redirect − control). Do not
  inflate N to "rescue" a null.
- **Ethics/IRB:** this is a new human experiment and **requires IRB/ethics approval before
  any data collection** (per `docs/datasets.md`). No data is collected in this phase — this
  is a *design* deliverable.

## 6. Decision this document makes

- **First public test (method validation):** E3 on **ds005494** (no new data).
- **First own experiment:** **CM-6H pre-Oracle** (E8 voluntary redirection; CONTROL /
  GENERAL REDIRECT / SPECIFIC CUE).
- **Next own experiment (queued):** E1 (affect induction → free thought), once the
  redirection method is validated.
- **THE ORACLE** (prediction reveal → veto → recursive prediction) is **NOT authorized**
  until the CM-6I readiness criteria are met.
