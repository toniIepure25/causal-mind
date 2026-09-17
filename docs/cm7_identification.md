# CM-7 — Causal Identification Document
## Open-Loop Encoding Stimulation → Cued Recall (OpenNeuro ds005494)

- **Status:** DRAFT — for orchestrator review before protocol freeze.
- **Date:** 2026-09-17 · **Author:** CAUSAL/STATS (CM-7)
- **Scope:** identification only. No analysis was run, no effect was estimated, and no
  stim-vs-nostim outcome difference was computed for this document. It specifies what is
  identifiable, under which assumptions, with which exclusions, and how the result must be
  labeled in the CM-6 counterfactual engine.
- **Dataset:** OpenNeuro ds005494, v1.0.1 — "Cued Recall of Paired Associates with
  Open-Loop Stimulation at Encoding or Retrieval" (Herrema & Kahana, CC0). N=20 subjects,
  26 sessions, iEEG + behavioral events. No published causal analysis of this dataset
  exists; CM-7 would be the first.
- **Companions:** `ds005494_audit.md` (authoritative audit, 2026-09-17 — all dataset facts
  below are taken from it and are NOT re-verified here), `cm6_identification_assumptions.md`
  (CM-6A methodology), `src/causal_mind/causal/counterfactuals.py` (engine, v0).

---

## 0. Verdict (up front)

**CONDITIONALLY IDENTIFIABLE** as an average causal effect, under assumptions A1–A5 (§6).
The primary estimand — the site-specific ATE of open-loop stimulation of the targeted
hippocampal/entorhinal electrode at encoding on subsequent cued recall of the stimulated
pairs, aggregated across subjects — is identified by list-level within-subject
randomization. The result must be labeled `experimentally_identified` in the CM-6
counterfactual engine with an attached `RandomizedEvidence` record; the engine refuses the
label without one (§12). If A1 (randomization executed as documented) fails, the claim
downgrades to observational and the estimand is not identifiable from this data alone
(§11). Top threats: T1 electrode-specificity of the intervention, T2 clinical population +
no sham, T3 nested/clustered effective sample size (§9).

---

## 1. Causal question & estimand

### 1.1 Causal question

Does delivering the documented open-loop biphasic stimulation train to the subject's
targeted hippocampal/entorhinal electrode during the encoding presentation of a word pair
**cause** that pair to be recalled better (or differently) at the subsequent cued-recall
test?

Formally this is the interventional contrast `P(Y_future | do(X=1))` vs
`P(Y_future | do(X=0))` — the CM-7 "future state" question: an intervention at encoding
changes the distribution of a future (recall-window) state. It is *not* the observational
association `P(Y | X=1)`, which equals the interventional distribution only because of the
randomization in §5.

### 1.2 Notation

- Subject `k = 1..20`; session `s`; list `l = 1..25` within a session (plus one practice
  list, list −1, excluded); pair `i = 1..6` within a list.
- `X_{kli} ∈ {0,1}`: the pair's encoding presentation received the stimulation train (1) or
  not (0).
- `x_{kl} ∈ {0,1}`: list `l` is an encoding-stim list (1) or a no-stim list (0).
  Retrieval-stim lists are excluded from the primary estimand (§10).
- `Y_{kli}`: the recall outcome for pair `i`. Primary: `Y ∈ {0,1}` = `correct`. Joint
  outcome: `(correct, resp_word, response_time)`.
- Potential outcomes: `Y_{kli}(1)`, `Y_{kli}(0)` — the recall outcome for pair `i` had its
  encoding been (not) stimulated, with everything else in the design held fixed.

### 1.3 Primary estimand — site-specific ATE at encoding

The **pair-level average treatment effect**, contextualized to encoding-stim lists,
aggregated across subjects:

```
ATE = E_k [ E_i [ Y_{kli}(1) − Y_{kli}(0)  |  list l is an encoding-stim list ] ]
```

- Inner expectation: over the 6 pairs of an encoding-stim list. All 6 pairs are *eligible*
  for stimulation; 3 receive it (alternating positions, phase randomized) and 3 do not.
- Outer expectation: over subjects `k` — the marginal (population) ATE across the 20
  subjects.
- `Y(1)` = recall outcome had the pair's encoding received the documented train (onset
  −200 ms, 4.6 s, 50 Hz, 230 pulses, 300 µs, targeted electrode).
- `Y(0)` = recall outcome had it not.
- **Site-specific** (A2): `do(X=1)` means "deliver the documented train to *this subject's
  targeted electrode*." The estimand is NOT "the effect of hippocampal stimulation in
  general."
- **Contextual**: `Y(0)` for a non-stimulated pair in an encoding-stim list is the
  counterfactual in a list where 3 of 6 pairs WERE stimulated (the list context is fixed by
  design). The estimand is the effect of stimulating a pair's encoding *given the
  encoding-stim list context*. If stimulation spills over to neighboring pairs, the
  estimand is a contextual total effect, not an isolated pair effect (§9 T3, §11).

### 1.4 Secondary estimand — distributional effect

The full shift in the recall distribution, not just the mean:

```
ΔP(A) = P( Y ∈ A | do(X=1) ) − P( Y ∈ A | do(X=0) ),   for all measurable A in the outcome space.
```

For the binary core (`correct`) this reduces to the ATE (§1.3); it becomes non-trivial for
the joint outcome `(correct, resp_word, response_time)`: the shift in recall probability,
in the latency distribution (`response_time`, among correct responses), and in the
distribution of recalled-word identity. It is identified under the same assumptions
(every cell of the outcome distribution is a function of the potential outcomes, and
randomization applies to the whole outcome vector).

### 1.5 CTE — causal treatment effect / persistence over the recall window

```
CTE = d( P(Y_rec | do(X=1)),  P(Y_rec | do(X=0)) )
```

where `Y_rec` is the recall-window outcome (the recall event: `correct` + `resp_word` +
`response_time`) and `d` is a chosen distributional metric (total variation for the binary
core; embedding-space distance if `resp_word` is embedded).

The "persistence" reading: the intervention occurs at encoding (t ≈ 0) and the effect is
measured at the future recall window (~1–2 min later); the CTE quantifies how much of the
interventional difference **persists** as a difference in the recall-window distribution.
Notes:

- The CM-6 implementation (`causal/metrics.py::causal_trajectory_effect`) computes a
  centroid distance between two sets of future-state vectors, optionally calibrated against
  a matched control. For this randomized contrast the two sets are the interventional
  outcome sets under `do(X=1)` and `do(X=0)`; the matched-control calibration (designed for
  an observational baseline) is **not applicable** — the randomization is the control.
- Within-window dynamics (the 5 s recall window) are not resolved as a trajectory; the
  latency (`response_time`) is the only within-window resolution the data provide.

### 1.6 Corroborating list-level contrast (a different estimand)

List-level: `ATE_list = E[ mean recall of an encoding-stim list − mean recall of a
no-stim list ]` (260 vs 130 lists). This is **not** the same estimand as §1.3: it is the
effect of "3 of 6 pairs stimulated at encoding" on the *average* recall of the list, and it
includes any spillover of stimulation onto the 3 non-stimulated pairs. It is identified by
the same randomization and is reported as a corroborating contrast, not the primary.

---

## 2. Treatment (X) definition

### 2.1 Pair level (primary)

`X_{kli} = 1` iff the pair's 4 s encoding presentation (the `STUDY_PAIR` row) received the
stimulation train; `X = 0` otherwise.

- Within an encoding-stim list: exactly 3 of 6 pairs have `X=1` (alternating positions,
  phase randomized); 3 have `X=0`.
- Within a no-stim list: all 6 pairs have `X=0`.
- `X` is a well-defined constant treatment within a subject: train parameters
  (anode/cathode labels, amplitude, 50 Hz, 230 pulses, 300 µs, 4.6 s, onset −200 ms) are
  fixed within a subject and logged per event.

### 2.2 List level (corroborating)

`x_{kl} = 1` iff list `l` is an encoding-stim list; `x_{kl} = 0` iff no-stim.
Retrieval-stim lists are excluded from the primary (§10).

### 2.3 Where X is carried in the data

- **`STIM_ON` rows:** one per delivered train; onset = item onset − 200 ms, duration =
  4600 ms; carry `anode_label, cathode_label, amplitude, pulse_freq, n_pulses,
  pulse_width, stim_duration`.
- **`stimulation` field on `STUDY_PAIR` rows:** 1 = event occurs during stimulation → the
  pair-level `X` directly.
- **`stim_list` field:** 1 = list has stimulation (at encoding *or* retrieval). **Caution:**
  `stim_list` does NOT distinguish encoding from retrieval. List type (enc-stim vs ret-stim
  vs no-stim) must be derived from `STIM_ON` timing relative to the trial phase
  (co-occurring with `STUDY_PAIR` → encoding; co-occurring with `REC_START`/`TEST_PROBE` →
  retrieval). Since no list has both types, list type is well-defined.
- The practice list (list −1) is excluded.

### 2.4 Consistency / no version problem

Within a subject, `do(X=1)` has a single version (fixed electrode, fixed parameters) → the
consistency assumption holds trivially within a subject. Across subjects the "treatment"
differs by electrode (hence A2 and T1).

---

## 3. Outcome (Y) definition

- **Primary:** `Y = correct` (0/1) — whether the pair was correctly recalled at the cued
  recall test.
- **Secondary:** `response_time` (s, from recall onset to vocalization — latency within the
  5 s window); `resp_word` (recalled word; `<>` = vocalization without a word — a coded
  value, part of the outcome, not missing data).
- `Y` is defined at the **pair level** and is pre-labeled on the `STUDY_PAIR` rows
  (verified against the corresponding `REC_EVENT` rows in the audit).
- `Y` is the outcome for the *pair*, not for the probe: which word of the pair is cued
  (`probe_word`) is randomized per pair by the design — a design variable, not a
  confounder; it is balanced across `X` by randomization.
- **Data-integrity gate (before any result is reported):** the pre-labeling on
  `STUDY_PAIR` must be re-verified against `REC_EVENT` for all 26 sessions (the audit
  verified a sample). Differential missingness of `Y` by `X` (e.g., more `<>`/missing
  recall labels on stim pairs) would break identification of the mean (§11).

---

## 4. Time order (why this is `P(Y_future | do(X))`)

- **X:** the stimulation train during the 4 s pair presentation — onset 200 ms before pair
  onset, 4.6 s duration, ending 400 ms after pair offset.
- **Y:** the cued-recall test of that pair — after the remaining pairs, 6 arithmetic
  distractors, and test orientation; ~1–2 min after the pair's encoding, in the same list;
  5 s per cue, random test order.
- For encoding-stim pairs, **X strictly precedes Y** (verified from event onsets in the
  audit). The intervention at encoding can affect recall only through its effect on the
  encoded memory trace (and any state it induces that persists to the test); there is no
  reverse-time path.
- This is exactly the CM-7 "future state" structure: `P(Y_future | do(X))` with
  `Y_future` = the recall-window state. The retrieval-stim contrast does **not** have this
  structure (X concurrent with Y; §10).

---

## 5. Identification basis

### 5.1 Causal structure

```
U_k  (subject: montage, electrode site, pathology, baseline memory, age, sex, hand)
   └─> Y
       (U_k ⊥ X: every X value occurs within every subject — within-subject design)

U_l  (list: word-pair set/difficulty, list position, carryover state from earlier lists)
   └─> Y
       (U_l ⊥ X: list-level randomization, A1)

serialpos, word difficulty, probe word   (pre-treatment; design-fixed or randomized)
   └─> Y
       (⊥ X: phase randomization, per-pair probe randomization, per-list test-order randomization)

X (stimulation at the pair's encoding)
   ├─> Y                    [the causal effect of interest]
   └─> M (arousal, attention, seizure, EEG state, subjective state)
           └─> Y            [mediators — post-treatment; excluded from adjustment, §7]

X_{l-1} (earlier list's stim) ─> M_{l-1} ─> U_l (carryover) ─> Y_l
       (X_l ⊥ U_l: the current list's X is randomized independently of the state)
```

There is **no backdoor path** `X → Y`: every common cause of `Y` (`U_k`, `U_l`,
pre-treatment pair variables) is independent of `X` by design (within-subject + list-level
randomization + phase/probe/test-order randomization). The only paths from `X` to `Y` are
the direct effect and post-treatment (mediator) paths.

### 5.2 Why this identifies the ATE

Under A1 (randomization executed as documented):

1. `(Y(1), Y(0)) ⊥ X` — unconditional exchangeability of potential outcomes and treatment
   assignment (randomization breaks every backdoor path, §5.1).
2. **Consistency:** the observed `Y` for a stimulated pair equals `Y(1)` (single treatment
   version, §2.4).
3. Therefore `E[Y(1)] = E[Y | X=1]` and `E[Y(0)] = E[Y | X=0]`, and

   **ATE = E[Y | X=1] − E[Y | X=0]**,

   computed at the pair level within encoding-stim lists (primary) and at the list level
   (corroborating), with clustered inference (§5.5).

Intuitively: same subject, same electrode, same session, same train parameters — the only
systematic difference between a stimulated pair and its non-stimulated neighbors is the
stimulation train itself. The same argument applies to every cell of the outcome
distribution (§1.4) and to the CTE (§1.5).

### 5.3 The randomized block design (10/10/5) preserves identifiability

The fixed quotas (10 enc-stim, 10 ret-stim, 5 no-stim per session) form a **randomized
block design**: the quotas constrain marginal counts, not the conditional independence of
`X` and the potential outcomes. Within an encoding-stim list the alternating phase is
randomized 50/50, so the stimulated positions (1,3,5 vs 2,4,6) are independent of `X`; any
fixed position × difficulty pattern is differenced out by the within-list contrast. The
design is not "some lists happen to be stimulated" — the assignment is random, and that is
what breaks the backdoor paths.

Minor audit caveat (carried into A1): the README documents random choice of 20 of 25
stimulation lists and random phase, but does not explicitly state that the 10-enc/10-ret
split itself is random. For the primary contrast the relevant randomization is the
assignment of lists to {enc-stim, no-stim} and the phase; the enc/ret split does not enter
the primary contrast (ret-stim lists are excluded, §10). The audit found list-assignment
patterns non-systematic in the data.

### 5.4 Positivity / overlap

Holds by design: within an encoding-stim list, `P(X=1) = P(X=0) = 3/6` (alternating); at
the list level both arms are non-empty in every session (10 vs 5 lists). No trimming needed.

### 5.5 Effective sample size (A3)

- 26 sessions × 25 lists = 650 lists: **260 enc-stim, 260 ret-stim, 130 no-stim**.
- Pairs: 3900 total; within enc-stim lists: **780 stim (X=1) vs 780 non-stim (X=0)** pairs;
  no-stim lists: 780 pairs (X=0).
- Pairs are nested in lists (3 per arm per enc-stim list), lists in sessions, sessions in
  subjects (20). Trial-level n (780/780) is **not** the effective n.
- Inference: the primary analysis uses the pair level with list (and subject/session)
  random effects — equivalently, the within-list contrast (mean of the 3 stim vs 3
  non-stim pairs within each enc-stim list; 260 lists) aggregated across subjects. The
  list-level corroborating contrast uses list-mean recall (260 vs 130 lists) with subject
  random effects.
- The point estimate of the ATE is design-consistent under randomization regardless of the
  clustering model; the clustering model determines the validity of the uncertainty
  (CI, p). Naive trial-level inference understates variance (T3).

---

## 6. Assumptions (numbered, explicit)

**A1 — Randomization executed as documented.** The list assignment (20 of 25 stimulation
lists: 10 enc, 10 ret, 5 none; no list has both) and the alternating phase (50/50
start-on/start-off) were actually randomized as documented. Sub-points: (a) assignment of
lists to {enc-stim, no-stim} is random within subject/session — required by the primary
contrast; the audit found the pattern non-systematic, but the randomization procedure
itself is as documented, not re-derivable from the data; (b) the phase is random; (c) no
implementation bias — the alternating design makes experimenter steering of stimulation to
"hard" pairs impossible by construction (positions are fixed-alternating).
*If A1 fails:* the contrast is observational; backdoor paths `X ← U → Y` reopen; the
estimand is not identifiable from this data without untestable ignorability (§11).

**A2 — The estimand is site-specific.** `do(X=1)` = "deliver the documented train to *this
subject's targeted electrode* (hippocampal or entorhinal; specific subfield/hemisphere/
depth)." Target electrodes vary across subjects (e.g., R1003P = left CA3 depth contacts),
so the estimand is "the average effect of stimulating the targeted electrode across the 20
subjects," **not** "the effect of hippocampal stimulation in general." Cross-subject
aggregation assumes the targeted sites are functionally comparable (hippocampus/entorhinal),
which is only approximately true (T1).

**A3 — Nested structure handled at the effective unit.** Pairs → lists → sessions →
subjects. Inference uses the list (or pair-within-list) as the effective unit with
subject/session random effects; trial-level n ≠ effective n (§5.5). The point estimate is
design-consistent; the clustering model is what makes the uncertainty valid.

**A4 — No unmeasured time-varying confounding of list assignment; carryover modeled.**
Randomization makes `X_l` independent of the state at the start of list `l` (including
carryover from earlier lists), so carryover does **not** confound the contrast — it is a
time-varying source of state that must be handled in the variance structure (list position;
a lagged list-type indicator is a pre-treatment variable for the current list and safe to
include as a variance control / heterogeneity probe). Carryover can only bias the contrast
if the randomization itself was state-dependent (adaptive assignment) — that is an A1
failure, not a carryover problem. The pair-level within-list contrast is additionally
robust to list-level carryover (differenced out within the list).

**A5 — No sham control.** The control is "no stimulation at all," not sham stimulation.
The identified effect is the **total effect of the delivered train** — the intended neural
effect plus any non-specific effects (arousal, expectation, sensation, micro-seizure
induction). The design cannot decompose these; the claim must be worded as the effect of
the delivered train, not of "hippocampal stimulation on memory" per se.

---

## 7. Post-treatment variables to EXCLUDE from adjustment

Conditioning on any of the following biases the total-effect estimand (mediator blocking
or collider bias). They must **not** appear in the adjustment set:

1. **iEEG signals** — all channels, all time points from stimulation onset onward. For the
   encoding-stim contrast, X precedes all subsequent EEG; EEG is post-treatment (a
   mediator of `X → Y`, and a collider if also caused by unmeasured subject state). The
   iEEG is not needed for the behavioral estimand at all.
2. **Arousal / attention state** (unmeasured; behaviorally proxied) — mediator on the
   `X → Y` path.
3. **Seizure / micro-seizure activity** — mediator (and a safety signal); conditioning
   blocks part of the effect and induces collider bias.
4. **Subjective state / expectation / awareness of stimulation** — mediator (subjects may
   feel the train; expectation is induced by X).
5. **Math-distractor performance** (the 6 arithmetic problems between encoding and
   recall) — post-encoding-stim, pre-recall; mediator / proxy for attention-arousal state.
6. **Recall-window behavior other than the recorded outcome** (vocalization dynamics,
   etc.) — part of Y or downstream of Y.
7. For the retrieval-stim contrast (if run, §10): everything measured after cue onset −
   200 ms (stim onset) — nearly the entire recall window is post-treatment.

Rule: the adjustment set may contain **only pre-treatment variables** (§8). Randomization
makes adjustment optional for validity; the pre-treatment covariates in §8 are included
for precision and carryover control, not for identification.

---

## 8. Confounders: handled by design vs by adjustment

| Confounder | Level | Pre/post-treatment | Handling |
|---|---|---|---|
| Montage, electrode site, pathology, baseline memory, age, sex, hand | subject | pre | **Design** — differenced out by within-subject design (all X values occur within each subject) |
| Session state (day-to-day) | session | pre (for the list) | **Design** — within-session contrast; session random effect |
| Word-pair set / list difficulty | list | pre | **Design** — balanced across conditions by list-level randomization (A1); list fixed effects optional |
| List position (order in session) | list | pre / time-varying | **Adjustment** — modeled (carryover, fatigue); not a confounder under A1, a variance control |
| Carryover state from earlier lists (arousal, attention, seizure risk) | list sequence | time-varying | **Modeling** — list position + lagged list-type indicator (pre-treatment for the current list, safe); heterogeneity probe |
| Serial position of the pair (1–6) | pair | pre | **Design** — balanced by phase randomization; optional adjustment for precision |
| Word difficulty (fixed pool) | pair | pre | **Design** — balanced by phase randomization (positions fixed-alternating, phase random); optional adjustment |
| Probe word (which word of the pair is cued) | pair | pre (randomized per pair) | **Design** — per-pair randomization |
| Test order (order of the 6 cues) | list | pre (randomized per list) | **Design** — per-list randomization |

Summary: subject/list/pair confounders are handled **by design** (randomization +
within-subject); list position and carryover are handled **by adjustment/modeling**
(variance control, heterogeneity probes). **Nothing requires adjustment for
identification** — randomization suffices; adjustment buys precision.

---

## 9. Threats to identifiability (top 3)

**T1 — Neural, not cognitive, intervention.** `do(X)` is "inject current into electrode
E." The causal effect is confounded with electrode site (subfield CA1/CA3/CA4, entorhinal
cortex, hemisphere, depth vs grid, proximity to epileptogenic tissue) and with the
biophysics of the train (amplitude — note the audit's unit flag: sidecar says "milliamperes"
but 1500.0 is physiologically consistent with µA; pulse parameters; contact geometry). The
estimand is electrode-specific (A2); cross-subject pooling assumes the targeted sites are
functionally comparable, which is only approximately true. *Consequence:* the claim is
"stimulating the targeted electrode," never "hippocampal stimulation."

**T2 — Clinical epilepsy population + no sham.** Subjects are an inferred
epilepsy-monitoring population (iEEG at clinical sites; the README does not state a
diagnosis); targeted tissue may lie in the resection/epileptogenic zone (stimulation may
interact with it); generalizability to healthy populations is limited. With no sham (A5),
non-specific effects (arousal, expectation, micro-seizure) are inseparable from the
intended memory effect. *Consequence:* the effect is the total effect of the delivered
train in this population; no decomposition, no generalization claim.

**T3 — Nested/clustered design + sequential carryover.** Trials are nested in lists, lists
in sessions, sessions in subjects; lists run sequentially, so stimulation on one list can
alter state (arousal, attention, seizure risk) during subsequent lists. Effective n is at
the list level (~260 enc-stim vs ~130 no-stim lists; 20 subjects), **not** the trial level
(780/780 pairs). Randomization protects the average contrast, but (a) inference must
cluster at the list/subject level (A3) and (b) list-order effects must be modeled (A4).
*Consequence:* naive trial-level inference yields anti-conservative CIs; power is set by
~390 lists and 20 subjects, not ~1560 pairs.

---

## 10. The retrieval-stim contrast (excluded from the primary)

On retrieval-stim lists the 4.6 s train (onset 200 ms pre-cue) is **concurrent with** the
5 s recall window — X is not before Y, it is *during* Y. Therefore:

- It is **not** a future-state contrast; it does not support `P(Y_future | do(X))` in the
  CM-7 sense.
- It is **excluded from the primary estimand** (§1.3) and from the list-level
  corroborating contrast (§1.6, which is enc-stim vs no-stim only).
- **Optional secondary:** a concurrent manipulation of the retrieval process (effect of
  stimulating during the recall attempt on that recall attempt), identifiable under the
  same assumptions A1, A3, A4, A5 (A2 likewise site-specific) by the same list-level
  randomization (260 ret-stim lists; within-list contrast of the 3 stimulated cues vs the
  3 non-stimulated cues). If reported at all, it is a separate estimand with its own label
  — never as a "future state" or encoding effect.
- Note: the post-treatment exclusion set differs for this contrast (§7.7): nearly
  everything during the recall window is post-treatment.

---

## 11. Verdict

**CONDITIONALLY IDENTIFIABLE** as an average causal effect, under A1–A5.

- The primary estimand (§1.3) is identified by list-level within-subject randomization:
  `ATE = E[Y|X=1] − E[Y|X=0]` at the pair level within encoding-stim lists, aggregated
  across subjects, with clustered inference (A3). The distributional estimand (§1.4) and
  the CTE (§1.5) are identified by the same argument.
- **Downgrades:**
  - **A1 fails** (randomization not executed, or not verifiable, as documented) → the
    contrast is observational; the estimand is **not identifiable** from this data alone
    (backdoor paths reopen; the relevant confounders are unmeasured subject/list state, so
    no measured adjustment set blocks them). The claim downgrades to
    `observational_only` (L1 association).
  - **A2 violated by over-claiming** (wording the result as "hippocampal stimulation" or
    general "memory enhancement") → the claim downgrades to the site-specific,
    train-specific estimand.
  - **A3 violated** (naive trial-level inference) → the point estimate is still the ATE,
    but the uncertainty is invalid; the claim downgrades (unreliable inference) until the
    clustered model is used.
  - **A4 violated** (e.g., state-dependent/adaptive assignment of lists, or a misspecified
    variance model with large unmodeled heterogeneity) → the list-level contrast is
    biased (adaptive assignment case) or its uncertainty is invalid (misspecification
    case); the claim downgrades. The pair-level within-list contrast is more robust
    (list-level carryover is differenced out within the list).
  - **A5** is not an identifiability failure but an interpretation limit: the effect is
    the total effect of the train (neural + non-specific); it cannot be decomposed without
    a sham.
- **What would make it NOT identifiable:** (a) evidence that list assignment or phase was
  not random (A1); (b) a consistency violation (the delivered train systematically
  differed from the documented one, or parameters varied within a subject in an
  outcome-correlated way); (c) differential missingness of `Y` by `X` (e.g., more
  `<>`/missing recall labels on stim pairs) — the mean is then unidentified without a
  missingness model; (d) large pair-level interference that makes the "stimulated pair"
  context inestimable (the estimand narrows to a contextual effect; §1.3).
- **Gate before any result is reported as validated:** the reviewer's leakage audit (per
  AGENTS.md) — in particular that no post-treatment variable (§7) enters the adjustment
  set, that the pre-labeled `Y` is re-verified across all 26 sessions (§3), and that
  inference clusters at the effective unit (A3).

---

## 12. Mapping to the CM-6 counterfactual engine

Engine: `src/causal_mind/causal/counterfactuals.py` (v0). Every `CounterfactualResult`
carries a `counterfactual_status` ∈ {`observational_only`, `partially_identified`,
`experimentally_identified`}; `_enforce` **raises** if `experimentally_identified` is
requested without a valid `RandomizedEvidence` record (`randomized=True`, `n > 0`), and if
`partially_identified` is requested without an identifiability audit of status
`identifiable`.

- **Required label: `experimentally_identified`** (via
  `IdentifiedCounterfactual.from_experiment`). This is a randomized intervention — not an
  observational association (hence not `observational_only`) and not an observational
  backdoor identification (hence not `partially_identified`; no backdoor proof is attached
  or needed — identification is by design, §5).
- **Required inputs:**
  - `RandomizedEvidence(experiment_id="ds005494-enc-stim", randomized=True, n=<effective
    n>, effect_estimate=<ATE>, ci_low=..., ci_high=..., notes=...)`.
    - `n` = the effective sample size at the inference unit (list level: 390 lists for the
      list-level contrast; 260 lists × 3 pairs/arm for the within-list pair contrast). The
      engine only checks `n > 0`, but the record must be honest: do **not** put the
      trial-level n (1560) in `n` without stating the unit in `notes`.
    - `notes` must cite: the randomization unit (list), the scheme (10/10/5 + phase 50/50),
      the source of the randomization evidence (dataset README + audit verification), and
      this identification document (A1–A5).
  - The **estimand string** must specify: site-specific, encoding, pair-level (stimulated
    pairs), contextual to encoding-stim lists, aggregated across subjects (§1.3).
  - `justification` must cite this document and the assumption set A1–A5.
  - **Treatment input:** pair-level `X` from `STIM_ON` rows / the `stimulation` field on
    `STUDY_PAIR` (§2.3). **Outcome input:** `correct` (and the joint outcome) from
    `STUDY_PAIR` (§3). **Randomization unit:** list (§5).
- **Refusal semantics:** if the randomization evidence is insufficient — A1 unverified
  (randomization procedure undocumented or contradicted by the data), the randomization
  unit mis-specified, or the `RandomizedEvidence` record missing/invalid — the engine must
  **refuse** to upgrade: the result stays `observational_only` (via
  `observational_result`). The refusal is enforced in code (`_enforce` raises); the
  analysis pipeline must treat a raised refusal as a hard stop, not a warning.
- **Retrieval-stim contrast** (if run, §10) gets its own `RandomizedEvidence` record and
  its own estimand string (concurrent retrieval manipulation) — also
  `experimentally_identified` (it too is randomized), but it must never be labeled a
  future-state / encoding effect.
- **Claim level:** a validated result under this protocol is an **L6** claim (causal
  evidence from valid intervention/identification) in `docs/claims_registry.md`, worded
  exactly as the site-specific, train-specific, population-limited estimand; the level can
  only be raised by a reviewer-approved gate pass.

---

## Appendix A. Data provenance (from the authoritative audit)

All dataset facts in this document are taken from `ds005494_audit.md` (2026-09-17,
RESEARCHER, CM-7 task 1) and are not re-verified here. Key items: paradigm and timings
(README + `events.tsv` onsets); intervention and parameters (`STIM_ON` rows);
randomization scheme (as documented; data pattern non-systematic); pair outcome
pre-labeled on `STUDY_PAIR` (cross-checked against `REC_EVENT`, sample); N=20 subjects /
26 sessions; no published causal analysis of this dataset exists (CM-7 would be the
first). Open audit flags carried into this document: amplitude unit (likely µA, not mA —
T1); whether the 10-enc/10-ret split itself is random (minor — A1); epilepsy population
inferred, not stated (T2).

## Appendix B. Open items for the orchestrator

1. Confirm the primary estimand is the **pair-level contextual ATE** (§1.3), not the
   list-level contrast (§1.6) — they are different estimands; this document recommends
   the pair-level as primary.
2. Confirm the effective-n convention for `RandomizedEvidence.n` (§12).
3. Confirm whether the retrieval-stim secondary (§10) is in scope for the frozen protocol.
4. Confirm the optional word-difficulty adjustment (requires pre-computing pair difficulty
   from the fixed word pool — a pre-treatment variable, safe).
5. Schedule the reviewer's leakage-audit gate (§11) before any result is reported as
   validated.
