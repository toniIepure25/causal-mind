# CM-6A — Candidate Causal Graph (Dynamic Cognitive SCM)

Generated: 2026-09-16 · Engine: CAUSAL/STATS (CM-6A) · **Red-team revised 2026-09-16 (CM-6J GO-WITH-CHANGES).**
Data: ds006067 think-aloud, 118 subjects, 6436 thoughts.
Machine-readable SCM: `reports/cm6_candidate_scm.json` · Full analysis: `reports/cm6_observational_results.json`.

> **Status banner.** This is a **candidate** graph built from **observational** data only.
> **0 of 84 candidate edges are CAUSALLY IDENTIFIED.** Every edge is at most
> CONDITIONALLY SUPPORTED or TEMPORALLY PRECEDENT. Nothing here is a causal discovery.
> The deliverable is the *set of antecedents worth experimentally perturbing* plus an
> explicit account of what is **unanswerable** from ds006067.

> **⚠ Artifact warning (CM-6J).** The 14 affect/sensory dimensions are **GPT-generated**
> (`rating_source = gpt_generated`), not measured. The headline "affect is the strongest
> antecedent" is **substantially inflated by between-subject GPT-rating baselines**: the
> *within-subject* (demeaned) lag-1 R² for the affect family is **tiny (0.01–0.05)**, while
> the *pooled* R² is high (joy 0.20) because GPT rates some subjects systematically
> higher than others. See §5.1 and §7. The genuine within-subject affect dynamics are real
> but weak. **Do not cite the pooled affect numbers as evidence that affect drives future
> thought within a person.**

## 1. What this is (and is not)

CM-5 established a frozen, red-team-validated **NULL**: HRF-safe fMRI adds no incremental
prospective value for future thought beyond behavior + nuisance. The project moves from
**FORECAST** to **EXPLAIN / INTERVENE**. The distinction that governs this document:

- **Prediction:** `P(T_future | history)` — what CM-2/CM-3/CM-5 measured (L2–L5).
- **Causation:** `P(T_future | do(X))` — what CM-6 needs (L6+).

A lagged association `X[t] -> Y[t+1]` is **not** a causal effect. It is a *candidate
antecedent* worth perturbing only if (a) temporally precedent, (b) survives conditioning,
(c) stable across subjects, and (d) a plausible intervention exists. This document ranks
candidates on (a)–(d) and states the identifiability of each.

## 2. Structural equation

```
Z[t+1] = f( Z[t], Z[t-1:t-k], context[t], latent_U[t] )
```

`Z` is the cognitive state vector (below). `context[t]` = topic/prompt. `latent_U[t]` is an
**unmeasured** common cause (subject trait, mood baseline, task engagement, unmodeled
stimulus features, and — critically — the **per-subject GPT-rating baseline**). The presence
of `latent_U[t]` is the single reason no edge is identifiable (§6, and
`cm6_identification_assumptions.md`).

## 3. Nodes (state dimensions)

| Node | Provenance | Type | Notes |
| --- | --- | --- | --- |
| `semantic_state` | model-inferred (frozen MiniLM, 384-d) | continuous | primary content representation |
| `topic` | directly observed (prompt) | discrete (8) | context, not a free state |
| `category` | directly observed (OSF) | discrete | coarse cognitive category |
| `emotional_intensity` | **model-inferred (GPT)** | continuous | affect magnitude |
| `joy, sadness, fear, anger, disgust, surprise, anxiety` | **model-inferred (GPT)** | continuous | affect family |
| `vision, audition, olfaction, gustation, somatosensation, interoception` | **model-inferred (GPT)** | continuous | sensory-modal family |
| `n_words, duration` | derived (deterministic) | continuous | linguistic load |
| `gap` | derived (deterministic) | continuous | inter-thought interval |
| `latent_U` | **unmeasured** | latent | common cause incl. GPT-rating baseline |

Each dimension appears at `t` (antecedent) and `t+1` (outcome). The SCM has 39 nodes and
124 directed edges.

## 4. Edge label taxonomy

- **ASSOCIATIONAL** — marginal co-variation only.
- **TEMPORALLY PRECEDENT** — `X[t]` precedes `Y[t+1]`; autoregressive; not yet conditioned.
- **CONDITIONALLY SUPPORTED** — `X[t] -> Y[t+1]` survives conditioning on the other
  dimensions at `t`, but is confounded by `latent_U`.
- **CAUSALLY IDENTIFIED** — identifiable under stated assumptions (backdoor adjustment
  exists **or** X randomized). **None qualify in ds006067.**
- **NOT IDENTIFIABLE** — no valid adjustment set; unmeasured confounding blocks it.

**Aggregate (124 edges):** ASSOCIATIONAL 40 · TEMPORALLY PRECEDENT 41 · CONDITIONALLY
SUPPORTED 39 · NOT IDENTIFIABLE 4 · **CAUSALLY IDENTIFIED 0.**

## 5. The seven observational analyses

### 5.1 Lagged predictive relationships (analysis 1) — read WITH the artifact warning
Out-of-sample lag-1 skill, subject-disjoint. **Two columns are reported because they differ
sharply:** *pooled* R² (all subjects together) and *within-subject* (demeaned) R² (the
genuine within-person dynamics).

| Dimension | pooled lag-1 R² | **within-subj R²** | between-subj share (η²) | floor frac | Reading |
| --- | --- | --- | --- | --- | --- |
| joy | 0.202 | **0.029** | 0.34 | 0.38 | pooled skill is a between-subject GPT-baseline artifact |
| anxiety | 0.105 | **0.048** | 0.14 | 0.62 | same; heavy floor mass |
| gustation | 0.175 | ~0.04 | — | — | **artifact**: GPT rates it near-constant |
| fear | 0.067 | **0.040** | 0.08 | 0.89 | weak within-subject; 89% at floor |
| sadness | 0.058 | **0.026** | 0.10 | 0.83 | weak within-subject |
| emotional_intensity | 0.054 | **0.014** | 0.13 | 0.00 | weak within-subject |
| vision | 0.053 | ~0.03 | — | — | sensory-modal persistence |
| n_words | 0.020 | ~0.02 | — | — | weak linguistic inertia |
| duration | 0.010 | ~0.01 | — | — | weak |
| gap | 0.007 | ~0.01 | — | — | weak |
| semantic_state | cos 0.303 | (decays with lag) | — | — | the CM-2/CM-3 signal |
| surprise / audition / somatosensation | ~0 / neg | ~0 | — | — | no skill |
| olfaction | 0 | 0 | — | — | no variance |

**Reading (corrected).** The *within-subject* dynamics — the quantity that would matter for
"changing X changes the future *within a person*" — are **weak across the board** (R²
0.01–0.05). The high *pooled* R² for joy/anxiety is dominated by **between-subject GPT-rating
baselines** (some subjects are rated systematically happier by the model), not by mood
inertia. The earlier "mood inertia / skill grows with lag" reading was **wrong**: for a
stationary within-subject process skill should *decay* with lag; the apparent increase was
baseline estimation (more lags → better estimate of the subject's stable mean). The only
robust within-subject signal is the **semantic embedding** (the CM-2/CM-3 prospective signal).

### 5.2 Conditional-independence structure (analysis 2)
Partial dependence of `X[t]` on `Y[t+1]` **given the other measured dimensions at time t**
(contemporaneous co-dimensions, *not* the lagged history — the conditioning set is
pre-treatment by construction), Fisher-z, n≈3868. **272 pairs tested; 39 survive BH-FDR
(q<0.05).**

- **duration[t] → gap[t+1]**: r_partial = **0.828**, p≈0 — the single strongest edge in the
  graph (a linguistic-load / pacing regularity, not a cognitive cause).
- **emotional_intensity[t] → joy[t+1]**: r_partial = 0.188, p≈0 — the strongest *affect* edge.
- **joy[t] → emotional_intensity[t+1]**: r_partial = 0.160; **duration[t] → n_words[t+1]**
  0.161; **n_words[t] → duration[t+1]** 0.159; **n_words[t] → gap[t+1]** −0.157.
- **anxiety[t] → fear[t+1]**: r_partial = 0.106.
- The large majority of pairs are conditionally independent given the co-dimensions.

**Reading.** Conditioning on the contemporaneous co-dimensions prunes most putative edges.
The surviving core is a **linguistic-load cluster** (duration ↔ n_words ↔ gap) plus a small
**affect core** (emotional_intensity ↔ joy, anxiety ↔ fear). The affect core is real but
small, and — per §5.1 — its *within-subject* strength is weak.

### 5.3 Partial information / incremental value (analysis 3)
Incremental R² of `X[t]` for `Y[t+1]` given all other antecedents at t:

- **duration[t] → gap[t+1]**: +0.2145
- **anxiety[t] → fear[t+1]**: +0.0459
- **emotional_intensity[t] → joy[t+1]**: +0.0320
- **fear[t] → anxiety[t+1]**: +0.0251; **joy[t] → emotional_intensity[t+1]**: +0.0242
- the rest: ≈ 0 or negative.

**Reading.** Most incremental information is in the **linguistic-load cluster** (duration →
gap). The affect core adds only a few hundredths of R². (Earlier draft's "all others ≈ 0"
was incorrect; the linguistic edges are the dominant incremental contributors.)

### 5.4 State-transition asymmetries (analysis 4)
Category→category transition matrix with directional asymmetry `P(i→j) − P(j→i)` (e.g.
2→4: 0.330 vs 4→2: 0.161, asym +0.169). **Descriptive only** — asymmetry of a transition
probability is a property of the stationary process, **not** evidence of causal direction.

### 5.5 Stability across subjects (analysis 5)
Per-subject lag-1 AR(1), reported as a distribution over 118 subjects:

| Dimension | mean AR(1) | frac positive | Note |
| --- | --- | --- | --- |
| emotional_intensity | 0.038 | 1.00 | stable but tiny |
| joy | 0.047 | 0.99 | stable but tiny (within-subj R² 0.029) |
| anxiety | 0.066 | 0.99 | stable but tiny |
| vision | 0.061 | 0.93 | stable |
| fear / sadness | 0.04 / 0.03 | 0.84 / 0.82 | mostly |
| gustation | 0.040 | 0.42 | artifact |
| olfaction | ~0 | 0.05 | no variance |

**Reading.** The affect core is *stable* (positive AR(1) in ~99% of subjects) but the
effect sizes are **tiny**. Stability of a tiny effect is not evidence of a strong dynamic.

### 5.6 Candidate mediator / moderator relationships (analysis 6)
Searched 126 `antecedent -> mediator -> target` triples. **10 triples** were flagged
`candidate_mediator=true` (all in the **linguistic → anxiety** cluster: duration/gap/n_words
→ anxiety), but **0 survive BH-FDR** across the 126-triple family. **No robust mediator is
identified.** (Mediation is also not identifiable here — §6.)

### 5.7 Counterfactual identifiability audit (analysis 7)
For each of the **84** candidate `X[t] -> Y[t+1]` edges, a backdoor-criterion check:
**n_identifiable = 0 / 84.** Every edge is **NOT IDENTIFIABLE** — `latent_U[t]` (now
explicitly including the per-subject GPT-rating baseline) is an unmeasured common cause, and
every backdoor-blocking set would have to include an unobserved node.

## 6. Which causal claims are UNANSWERABLE from ds006067

Because `latent_U[t]` (trait, mood baseline, engagement, unmodeled stimulus features, and
the **per-subject GPT-rating baseline**) is an unmeasured common cause of all measured
dimensions, the following are **unanswerable** from this data, no matter how large N is:

1. **Does inducing affect (do(joy↑)) change the future thought?** — confounded by baseline
   mood *and* by the GPT-rating baseline. The observed joy[t]→joy[t+1] association is
   consistent with "joy causes later joy," "a stable cheerful subject is cheerful at t and
   t+1," **and** "GPT rates this subject's sentences happier throughout."
2. **Does a semantic cue / memory cue / goal / attentional instruction redirect thought?** —
   none is randomized in ds006067.
3. **Mediation** (affect → mechanism → future thought) — not satisfiable here.
4. **Any individual-level causal effect** — needs subject-level randomization.

**What IS answerable (and is reported):** the *predictive* structure (lagged skill,
conditional dependence, incremental value, transition statistics, stability) — L1–L5 claims.
They identify *which X to perturb*, not what perturbing X does.

## 7. Caveats and known artifacts

- **GPT-rating baseline artifact (SEVERE; the #1 CM-6J finding).** The affect/sensory dims
  are GPT-generated. Independent recomputation (all 118 subjects) shows the *within-subject*
  lag-1 R² for the affect family is **0.01–0.05** (joy 0.029, anxiety 0.048,
  emotional_intensity 0.014), while the *pooled* R² is 0.05–0.20 — the gap is between-subject
  GPT-rating baselines (η²≈0.34 for joy). Bounded 1–4 scales with heavy floor mass (joy 38%,
  anxiety 62%, fear 89%, sadness 83% at the floor) further inflate apparent skill.
- **GPT vs human validation (18-subject subset).** GPT–human agreement is moderate and
  biased: **joy** Pearson 0.613 with GPT mean **1.695 vs human 1.196 (+0.50 inflation)**;
  **anxiety** Pearson **0.356** (weak) with +0.27 inflation; emotional_intensity 0.707. GPT
  ratings are **biased proxies, not measurements** — the same skepticism applied to
  gustation must apply to the whole affect family.
- **Consequence for the ranking.** The *genuine* within-subject affect dynamics are real but
  weak. E1 (affect induction) remains scientifically motivated **by the literature**, but its
  *observational* support in ds006067 is **far weaker than the pooled numbers suggest**, and
  must not be cited as "the strongest edge."
- **Topic is a coarse prompt** (8 values); it is context, not a manipulable antecedent.
- **Stationarity assumed within a scan** (~10 min); fatigue/learning not modeled.
- **Multiplicity.** 272 CI pairs + 126 mediator triples. BH-FDR (q<0.05): **39 CI edges
  survive, 0 mediator triples survive.** The composite candidate ranking uses arbitrary
  weights and is **hypothesis-generating**, not confirmatory.

## 8. Candidate antecedents worth perturbing (feeds CM-6C)

Ranked by (observational support, **corrected for the artifact**) × plausibility of a clean
intervention. **The ranking is hypothesis-generating; no edge is causally identified.**

| Rank | Antecedent X | Corrected obs. support | Edge id | Plausible clean intervention? |
| --- | --- | --- | --- | --- |
| 1 | **voluntary redirection** | none (the gap) | E8 | **no public data — requires our own CM-6F/H experiment** |
| 2 | **affect (joy / anxiety / emotional intensity)** | weak *within-subject* (R² 0.01–0.05); strong *pooled* = GPT-baseline artifact | E1 | **yes** — affect induction / emotional framing is a mature, randomized paradigm (motivated by literature, not by ds006067) |
| 3 | **memory cue** | conceptual | E3 | yes — cued recall / Think-No-Think (public: ds005494) |
| 4 | **semantic cue / prime** | conceptual | E2 | yes — semantic priming |
| 5 | **goal / task-set** | conceptual | E4 | yes — goal induction / language switch (public: ds006240) |
| 6 | **linguistic load (duration / n_words / gap)** | strongest *robust* obs. signal (duration→gap r=0.828, FDR-surviving) | — | weakly manipulable; mostly a pacing regularity |
| 7 | attentional cue / expectation / suppression | conceptual | E5/E6/E7 | partial (public outcomes are RT, not free thought) |

**Bottom line.** The single cleanest first *causal* edge to test is **E8 (voluntary
redirection)** via the CM-6H pre-Oracle experiment — it is the north-star gap and has the
cleanest within-subject baseline + randomized intervention + clean outcome. **E1 (affect)**
is the strongest *literature-motivated* cognitive edge and the best public-data handle is
ds006583 (affect→affect); the only public dataset with a genuinely randomized `do(X)` →
future semantic state is **ds005494** (E3, memory cue). The robust *observational* signal is
the **linguistic-load cluster** and the **semantic embedding**, not the affect family.

---

**Anti-HARKing / freeze.** The candidate node/edge set, the 7 analyses, the edge-label taxonomy, the BH-FDR family, and the hypothesis-generating ranking are frozen as of commit f3348dc (CM-6 baseline). Any change after seeing downstream experiment outcomes requires a new ADR + research-log entry and must not be used to retrofit a causal claim.
