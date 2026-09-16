# CM-6B — Public Intervention Dataset Audit

Audited: 2026-09-16 · Auditor: RESEARCHER agent (CM-6B)
Scope: PUBLIC datasets (behavioral / EEG / iEEG / fMRI) containing a **randomized or
experimentally manipulated variable X** that could shift a **subsequent cognitive /
verbal / semantic state**.

> **Verification method.** Every dataset below was verified with `webfetch` against the
> authoritative OpenNeuro public S3 bucket
> (`https://s3.amazonaws.com/openneuro.org/<ds>/dataset_description.json` and
> `participants.tsv`) and, where available, the GitHub mirror README
> (`github.com/OpenNeuroDatasets/<ds>`). Discovery used the GitHub repository search API
> scoped to the `OpenNeuroDatasets` org (title match). `api.openneuro.org` was
> **unreachable** from this environment (transport error) and the OpenNeuro web search is a
> JS app, so OpenNeuro discovery was done via the GitHub mirror + direct S3 metadata.
> Anything I could not confirm is explicitly marked **UNVERIFIED** and its feasibility is
> lowered. No dataset, N, license, or URL below is invented.

---

## 1. Why this audit (prediction != causation)

CM-5 established a frozen, red-team-validated **NULL**: HRF-safe fMRI adds no incremental
prospective value for future thought beyond behavior + nuisance. The project therefore
moves from **FORECAST** to **EXPLAIN / INTERVENE**.

The core distinction:

- **Prediction:** `P(T_future | history)` — what CM-2/CM-3/CM-5 did (L2–L5).
- **Causation:** `P(T_future | do(X))` — what CM-6 needs (L6+).

CM-6A (observational candidate SCM on ds006067) ranked the antecedent dimensions most
worth perturbing. **Corrected for the GPT-rating-baseline artifact (CM-6J):** the *pooled*
lagged association is strongest for the **affect family** (joy lag1 R²≈0.20, anxiety ≈0.11),
but this is dominated by **between-subject GPT-rating baselines** — the *within-subject*
lag-1 R² is only **0.01–0.05** (joy 0.029, anxiety 0.048). The robust *observational* signal
is the **linguistic-load cluster** (duration→gap r_partial=0.828, FDR-surviving) and the
**semantic embedding**; the affect family's genuine within-person dynamics are weak. Affect
remains a top *intervention* candidate **on literature grounds** (a mature, randomized
paradigm), not on ds006067 observational grounds. The candidate causal edges to test with a
real intervention are:

| Edge id | Candidate edge | CM-6A observational support |
| --- | --- | --- |
| E1 | **affect → future thought** | weak within-subject (GPT-baseline artifact); literature-motivated |
| E2 | semantic cue → future thought | conceptual (priming/association) |
| E3 | memory cue → future thought | conceptual (cueing/retrieval) |
| E4 | goal → future thought | conceptual (goal induction) |
| E5 | attentional cue → future thought | conceptual (Posner) |
| E6 | expectation/prior → future thought | conceptual (prediction error) |
| E7 | inhibitory control / thought suppression → future thought | conceptual (white bear) |
| E8 | voluntary thought redirection | **the CM-6F gap** (no public data) |

### The filter (what qualifies a dataset)

A dataset is only useful for CM-6 if it passes **both**:

1. **Randomized / manipulated X** — a variable that was assigned (subject-, trial-, or
   block-level), not merely observed. This is what makes `do(X)` identifiable.
2. **A FUTURE cognitive / semantic state as the outcome** — the measured outcome must be a
   *subsequent cognitive state* (a thought, a recalled/produced word, ongoing thought
   content, an affective state), **not** just a reaction time, accuracy, or a BOLD/ERP
   amplitude in a pre-specified ROI.

Most public cognitive datasets fail filter #2 (they measure RT/accuracy/BOLD). That
scarcity is itself a key finding of this audit (see §5).

---

## 2. Candidate table

Relevance (0–10) = how cleanly the dataset tests **one** of E1–E7 with a *future
cognitive/semantic state* outcome, weighted toward E1 (affect) and E3 (memory cue).

| # | Dataset (OpenNeuro) | Repo (verified) | License | N | Manipulated X | Randomized? (unit) | Outcome | Temporal res. | Future cog/sem state? | Causal effect identifiable? | Download size | Feasibility | Relevance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **Cued Recall of Paired Associates w/ Open-Loop Stimulation** (ds005494) | openneuro.org/datasets/ds005494 | CC0 | 20 | Open-loop electrical stimulation (hippocampus/entorhinal) at encoding **or** retrieval; + memory cue (cue word → associate) | **Yes** (list-level; 20/25 lists randomized: 10 enc, 10 ret, 5 none) | **Vocal cued recall** of paired-associate word (semantic state) | trials (4 s pairs, 5 s recall); iEEG ms | **Yes** (retrieved semantic state) | **Yes** (randomized stimulation → recall) | not measured (iEEG, 20 subj) | medium (iEEG-BIDS, re-reference) | **8** |
| 2 | **Using Music to Measure Affective Transitions** (ds006583) | openneuro.org/datasets/ds006583 | CC0 | 43 | Music (affect induction), assigned per participant | partial (tracks assigned; randomization not confirmed) | **Affective transitions** (affect over time) + self-report | continuous (affect sampled over time) | **Partial** (future *affective* state, not free semantic thought) | partial (music assigned; outcome = affect) | not measured | easy–medium (BIDS) | **6** |
| 3 | **PEERS — Penn Electrophysiology of Encoding & Retrieval** (ds004395) | openneuro.org/datasets/ds004395 | CC0 | ~200+ (large iEEG cohort; many n/a placeholders) | Encoding conditions in paired-associates task | partial (encoding condition assigned) | **Retrieval** (recall/recognition; semantic state) | trials; iEEG ms | **Yes** (retrieved semantic state) | partial (encoding assigned, not a clean per-trial randomized cue) | large (iEEG) | medium (iEEG-BIDS, large) | **6** |
| 4 | **Multi-session simultaneous EEG-fMRI w/ online experience sampling** (ds007216) | openneuro.org/datasets/ds007216 | CC0 | 24 (desc; tsv lists 25) | Task context: sustained attention (GradCPT) vs rest | partial (task order/context) | **Ongoing thought content** via multi-dimensional experience sampling (mood + thought content) | continuous (experience sampling) | **Yes** (free thought content — best free-thought outcome) | partial (task context assigned, not a clean per-trial randomized cue) | not measured (simul. EEG-fMRI) | medium (complex simultaneous EEG-fMRI) | **6** |
| 5 | **Bilingual speech production in language switching** (ds006240) | openneuro.org/datasets/ds006240 | CC0 | not confirmed (participants.tsv 404 at root) | Language to produce (L1/L2 switch) = goal/task-set | yes (trial/block language assignment, typical) | **Speech production** (verbal/semantic state) | trials | **Yes** (produced verbal state) | yes (language instruction assigned) | not measured | medium | **5** |
| 6 | **ERP priming: fingerspelling/print/signs in deaf readers** (ds005565) | openneuro.org/datasets/ds005565 | CC0 | 24 | Prime (fingerspelling / print / sign) = associative/semantic prime | yes (trial-level prime) | ERP + behavioral (lexical decision/RT) | trials; EEG ms | **No** (ERP to probe, not a free thought) | yes (prime randomized) | not measured (EEG) | easy (EEG-BIDS) | **3** |
| 7 | **YOTO — multisensory perception & mental imagery EEG** (ds005815) | openneuro.org/datasets/ds005815 | CC0 | 20 | Sensory cues (visual / auditory / combined) | yes (trial-level cues) | Vividness ratings + ERPs (mental imagery) | trials; EEG 1000 Hz | **No** (vividness rating, not a free thought) | yes (cues randomized) | not measured (EEG) | easy (EEG-BIDS) | **3** |
| 8 | **iEEG on children during Stroop task** (ds004859) | openneuro.org/datasets/ds004859 | CC0 | not confirmed | Stroop congruency (congruent/incongruent) = inhibitory control | yes (trial-level) | RT / accuracy (color naming) | trials | **No** (RT) | yes | small (43 KB git repo) | easy | **2** |
| 9 | **Expectation effects on repetition suppression in nociception** (ds006374) | openneuro.org/datasets/ds006374 | CC0 | not confirmed | Expectation (pain cue) | yes (trial-level) | Pain (nociception) + BOLD repetition suppression | trials | **No** (pain, not a thought) | yes | not measured | medium | **1** |

**Found via GitHub title search but NOT fully verified via S3** (listed for completeness;
treat as UNVERIFIED, lower feasibility):

| Dataset (OpenNeuro) | Title (from GitHub mirror) | Why noted / why not a top candidate |
| --- | --- | --- |
| ds006131 | PAFIN: PennLINC **Affective** Instability (+ derivatives ds006143/182/185/190/193) | Affect-related fMRI, but clinical affective-instability cohort, not a randomized affect → future-thought design |
| ds006866 | Discrepancy between self-report and neurophysiological markers of **socio-affective** responses in lonely individuals | Affect-related; observational/clinical, not a clean randomized X → future thought |
| ds005468 | Coordinated Representations for Naturalistic **Memory Encoding and Retrieval** in Hippocampal Neural Subspaces | iEEG hippocampal memory; related to E3 but not verified (N, X, outcome unconfirmed) |
| ds005059 | PAL1 (referenced inside ds005494 README as its non-stimulation base) | The non-stimulation paired-associates iEEG dataset; related to #1/#3 but not independently verified here |
| ds007420 | Multi-Distance fNIRS … Ball-Squeezing and Motion-Artifact Induction | "induction" = motion artifact, not affect; not relevant |
| ds007952 | Visual Aesthetic Value under Continuous Flash Suppression | "suppression" = perceptual CFS, not retrieval/thought suppression; not relevant |
| ds006812 | Constrained optimized water suppression for 1H MRS | "suppression" = MRS water suppression; not relevant |

---

## 3. Per-dataset notes (strongest candidates)

### #1 ds005494 — Cued Recall of Paired Associates with Open-Loop Stimulation (iEEG, N=20, CC0)
**The cleanest public `do(X) → future semantic state` I found.** Verified via S3
`dataset_description.json` + `participants.tsv` (20 rows) + full GitHub README.

- **Design (from README):** participants study pairs of visually presented words →
  arithmetic distractor → **cued recall** (one word of a pair shown; participant *vocally
  recalls* the other; 5 s per cue). 25 lists/session.
- **The intervention:** **open-loop electrical stimulation** of a single electrode
  (hippocampus / entorhinal cortex) delivered at **encoding or retrieval**. **20 of 25
  lists are randomly assigned as stimulation lists** (10 encoding-stim, 10 retrieval-stim,
  5 no-stim); no list has both. Stimulation timing/parameters are logged in the events TSV.
- **Why it fits CM-6:** it contains **two** candidate structures at once:
  - **E3 (memory cue → future semantic state):** the cue word is the X; the *recalled
    associate* is the future semantic state.
  - **A genuine randomized `do(X)`:** stimulation is randomly assigned to lists, so the
    causal effect of stimulation on subsequent recall is **identifiable** (the gold-standard
    intervention structure the project wants).
- **Caveats (honest):** (a) **iEEG** — intracranial, clinical epilepsy patients, unique
  montages, must be re-referenced; not generalizable to scalp EEG/fMRI. (b) The "future
  thought" is a **cued recall** (a *retrieved* semantic state), not a free/spontaneous
  thought. (c) N=20. (d) The primary X is a **neural** intervention (stimulation), not a
  cognitive X (affect/semantic cue).
- **Verdict:** best available public dataset matching `P(T_future | do(X))` with a
  semantic-state outcome; use as a **methodological template** and as the E3 (memory-cue)
  test, not as the E1 (affect) test.

### #2 ds006583 — Using Music to Measure Affective Transitions (N=43, CC0, eNeuro 2025)
Verified via S3 `dataset_description.json` + `participants.tsv` (43 rows: sub-musevent01–47,
gaps at 35/36/40/43). Authors Sachs, Kozak, Ochsner, Baldassano; DOI
10.1523/ENEURO.0184-24.2025.

- **Why it fits:** closest public dataset to **E1 (affect → future state)**. Music is used
  as an **affect induction** (the manipulated X); the outcome is **affective transitions**
  (how affect changes over time) — a *future affective state*.
- **Caveats (honest):** (a) the outcome is **affect**, not a free *semantic* thought — so it
  tests "affect induction → future affective state," a neighbor of E1, not E1 itself.
  (b) **Modality not confirmed** in the BIDS `dataset_description.json` (no `Data_Types`
  field); the eNeuro 2025 paper is the reference — **verify modality (likely fMRI) before
  use.** (c) Randomization of track assignment not confirmed from metadata.
- **Verdict:** the best public handle on the **affect family** (the project's strongest
  observational edge), but the outcome is affect, not a free thought.

### #3 ds004395 — PEERS, Penn Electrophysiology of Encoding and Retrieval (iEEG, N≈200+, CC0)
Verified via S3 `dataset_description.json` + `participants.tsv` (sub-LTP063–LTP440, ~378 IDs
with many `n/a` placeholders/exclusions; exact analyzed N not confirmed). Kahana lab.

- **Why it fits:** large **iEEG** paired-associates **encoding → retrieval** dataset.
  Retrieval (recall/recognition) is a **future semantic state** (E3). Large N and ms
  temporal resolution.
- **Caveats:** (a) iEEG clinical cohort. (b) The "X" is the **encoding condition**, not a
  clean per-trial randomized cue, so identifiability is weaker than ds005494. (c) Exact N
  and the specific encoding manipulations need confirmation from the README/paper.
- **Verdict:** strong large-N E3 (memory) resource; secondary to ds005494 for a clean
  `do(X)`.

### #4 ds007216 — Multi-session simultaneous EEG-fMRI with online experience sampling (N=24, CC0)
Verified via S3 `dataset_description.json` + `participants.tsv` (25 IDs; description says
24 — one likely excluded). Authors Kucyi, Shareef-Trudeau, … Li (Drexel).

- **Why it fits:** the **best "free thought state" outcome** in this audit. Multi-dimensional
  **experience sampling** captures **ongoing thought content + mood** over time during
  sustained attention (GradCPT) and rest — i.e., a genuine free cognitive/affective state
  stream, closest in spirit to ds006067's think-aloud thoughts.
- **Caveats:** (a) the X is **task context** (attention vs rest), not a clean randomized
  per-trial cue/affect manipulation → weak identifiability for a specific edge. (b)
  Simultaneous EEG-fMRI is complex to parse. (c) N=24.
- **Verdict:** best for studying **free ongoing thought states** and as a bridge to
  ds006067; not a clean single-edge intervention test.

### #5 ds006240 — Bilingual speech production in language switching (CC0)
Verified via S3 `dataset_description.json` (N not confirmed — `participants.tsv` 404 at
root; Wolna & Wodniecka).

- **Why it fits:** **E4 (goal/task-set → future verbal state).** The instruction of *which
  language to produce* is a goal/task-set manipulation (typically trial/block-randomized);
  the **produced speech** is a subsequent verbal/semantic state.
- **Caveats:** bilingual-specific; the "thought" is the produced word (constrained by the
  task), not a free thought; N and exact randomization unit unconfirmed.
- **Verdict:** reasonable E4 (goal) test with a verbal-state outcome; lower priority.

---

## 4. Ranked recommendation — best "first public intervention test"

Ranked by how cleanly one dataset tests **one** candidate edge with a **future
cognitive/semantic state** outcome and an **identifiable** causal effect:

1. **ds005494 (Cued Recall + Open-Loop Stimulation, iEEG, N=20) — RECOMMENDED FIRST TEST.**
   The only public dataset here with a **genuinely randomized `do(X)`** (open-loop
   stimulation, randomly assigned to 20/25 lists) **and** a **future semantic-state
   outcome** (vocal cued recall). It directly instantiates `P(T_future | do(X))` and also
   carries the **E3 memory-cue → future semantic state** structure (cue word → recalled
   associate). Use it to (a) validate the CM-6 intervention-analysis pipeline on a
   randomized design, and (b) test E3. *Accept the caveats:* iEEG clinical cohort,
   retrieved (not free) semantic state, N=20, and the primary X is neural (stimulation),
   not a cognitive X.

2. **ds006583 (Music → Affective Transitions, N=43) — best for the AFFECT edge (E1).**
   The project's strongest observational edge is affect; this is the closest public
   affect-induction → future-state dataset. *Caveat:* outcome is affect, not a free
   thought; confirm modality + randomization before use.

3. **ds007216 (EEG-fMRI + experience sampling, N=24) — best free-thought-state outcome.**
   Ongoing thought content + mood sampled over time; the closest public analog to
   ds006067's free thoughts. *Caveat:* X is task context (weak identifiability).

4. **ds004395 (PEERS, iEEG, N≈200+) — large-N E3 (memory) resource.** Encoding →
   retrieval with a semantic-state outcome; weaker identifiability than ds005494.

5. **ds006240 (Bilingual language switching, CC0) — E4 (goal → verbal state).** Goal/
   task-set manipulation → produced speech.

**Single best "first public intervention test": ds005494.** It is the only audited public
dataset where a *randomized* manipulation is followed by a *measured future semantic
state*, which is exactly the `P(T_future | do(X))` structure CM-6 requires. If the
priority is specifically the **affect** edge (E1), pair it with **ds006583** — but note
that no public dataset cleanly tests *affect → free future thought* (see §5).

---

## 5. What is NOT available (the gaps)

These are the honest negative findings — paradigms the project cares about for which I
could **not** verify a clean public dataset with a *future free cognitive/semantic state*
outcome:

- **No public dataset directly measures voluntary redirection of a predicted thought (E8).**
  Nothing public combines a *revealed prediction* with a *participant-initiated
  redirection* verified by trajectory divergence. **This is precisely the gap CM-6F must
  fill with new data.**
- **No verified public Think/No-Think / retrieval-suppression dataset with a free-recall
  outcome.** Searched OpenNeuro (GitHub mirror) for "suppression", "forget", "forgetting",
  "retrieval": the only memory-retrieval hits are *cued recall* (ds005494, ds004395,
  ds005468) and hippocampal encoding/retrieval — **no intentional-forgetting /
  Think-No-Think paradigm** with a public free-recall outcome was found. (Classic
  Anderson et al. T/N-T raw data not confirmed public.)
- **No verified public affect-induction → *free future thought* dataset.** The closest is
  ds006583 (music → *affective* transitions), but the outcome is affect, not a free
  semantic thought. No dataset randomizes an affect manipulation and then measures a
  subsequent *free* thought report.
- **No verified public thought-suppression ("white bear" / ironic process) dataset** with a
  thought-report (intrusion) outcome.
- **No verified public Posner-cueing → free-thought dataset** (Posner outcomes are RT).
- **No verified public emotional-framing (gain/loss) → free-thought dataset** (framing
  outcomes are decisions).
- **No verified public goal-induction → free-thought dataset** (closest: ds006240 language
  switching → produced speech, a constrained verbal state).

**Meta-finding:** the *future free cognitive/semantic state* filter is very restrictive.
Almost all public cognitive datasets measure RT, accuracy, BOLD amplitude, or ERP — not a
free "next thought." The datasets that do measure a retrieved or free semantic state
(ds005494, ds004395, ds007216) pair it with an X that is a **neural stimulation**, an
**encoding condition**, or a **task context** — not the clean *cognitive* X (affect,
semantic cue) the project's top edges require. **Consequently, the highest-value edges
(E1 affect → free thought, E8 voluntary redirection) cannot be validated on existing
public data and require the project's own CM-6F experiment.** Public data can validate the
*method* (ds005494) and partially test E3 (memory) and the affect *family* (ds006583).

---

## 6. Verification status

**Verified via webfetch (S3 `dataset_description.json` + `participants.tsv`, and GitHub
README where noted):**

| Dataset | S3 description | S3 participants (N) | GitHub README |
| --- | --- | --- | --- |
| ds005494 | yes | yes (20) | **yes (full paradigm)** |
| ds006583 | yes | yes (43) | no README in repo |
| ds004395 | yes | yes (~200+, many n/a) | not fetched |
| ds007216 | yes | yes (24/25) | not fetched |
| ds006240 | yes | **no (404 at root)** | not fetched |
| ds005565 | yes | yes (24) | not fetched |
| ds005815 | yes | via README (20) | **yes** |
| ds004859 | yes | not fetched | not fetched |
| ds006374 | yes | not fetched | not fetched |

**Found via GitHub title search but NOT verified via S3 (UNVERIFIED — lower feasibility):**
ds006131 (PAFIN) + derivatives, ds006866, ds005468, ds005059 (PAL1), ds007420, ds007952,
ds006812.

**Known environment limitations (affect confidence, not the datasets):**
- `api.openneuro.org` unreachable from this environment (transport error); OpenNeuro web
  search is a JS app. Discovery therefore relied on the GitHub `OpenNeuroDatasets` mirror
  (title match only) + direct S3 metadata. Title-based search **misses** datasets whose
  paradigm keyword is not in the title, so this audit is **not exhaustive** of OpenNeuro.
- Download sizes were **not measured** (would require S3 bucket listing, unavailable via
  webfetch); check each OpenNeuro dataset page for total size before acquisition.
- ds006583 modality and ds006240 N are **unconfirmed** — verify before use.
