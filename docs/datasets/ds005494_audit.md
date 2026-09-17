# ds005494 — Authoritative Audit (CM-7 Public Intervention Method Validation)

- **Audited:** 2026-09-17
- **Auditor:** RESEARCHER (CM-7, task 1)
- **Dataset:** OpenNeuro ds005494 — "Cued Recall of Paired Associates with Open-Loop Stimulation at Encoding or Retrieval"
- **Sources used (all fetched live on audit date):**
  1. OpenNeuro public S3 bucket `s3.amazonaws.com/openneuro.org` — `dataset_description.json`, full bucket listing (370 objects with sizes), `participants.tsv`, `stimuli/wordpools/wordpool_EN.txt`, per-subject BIDS sidecars and `events.tsv` (sub-R1003P/ses-0).
  2. GitHub mirror `OpenNeuroDatasets/ds005494` (branch `main`) — `README`, `CHANGES`, `participants.tsv`, `participants.json`, BIDS tree, `beh.json`/`events.json` sidecars, iEEG sidecar JSONs, `electrodes.tsv`, repo metadata (created 2024-09-17, last push 2024-09-25).
  3. Publication search — PubMed E-utilities (esearch/esummary), OpenAlex (author works for Haydn G. Herrema, A5107494647), bioRxiv search, Semantic Scholar (rate-limited, partial).
  4. **NOT reachable from audit environment:** `api.openneuro.org` (repeated transport errors) and the JS-only `openneuro.org` dataset page. Snapshot/version therefore verified via `DatasetDOI` + `CHANGES` + GitHub mirror (see Verification status).

---

## 1. Field-by-field audit

| Field | Verified value | Source |
|---|---|---|
| Exact name | "Cued Recall of Paired Associates with Open-Loop Stimulation at Encoding or Retrieval" | S3 `dataset_description.json`; GitHub `README` |
| Snapshot / version | **v1.0.1** (latest). v1.0.0 = 2024-09-17 initial release (20 participants, 26 sessions); v1.0.1 = 2024-09-25 (added participant metadata) | `DatasetDOI: doi:10.18112/openneuro.ds005494.v1.0.1` (S3 `dataset_description.json`); `CHANGES` (GitHub); GitHub repo last push 2024-09-25 |
| Authors | Haydn G. Herrema, Michael J. Kahana (Computational Memory Lab, U. Pennsylvania) | S3 `dataset_description.json`; `README` |
| License | **CC0** | S3 `dataset_description.json` |
| BIDS version / type | BIDS 1.7.0, `DatasetType: raw` | S3 `dataset_description.json` |
| Funding | DARPA RAM: N66001-14-2-4032 | S3 `dataset_description.json` |
| Number of subjects | **20** (`sub-R1003P … sub-R1185N`); **26 sessions** total (R1003P:2, R1016M:3, R1031M:2, R1060M:2, R1111M:2, all others:1) | `participants.tsv` (20 rows); GitHub tree (20 `sub-*` dirs); `CHANGES`; S3 listing (26 `beh.tsv` files) |
| Subject demographics | Age 20–57; 9 F / 11 M; 19 R, 1 L (R1036M) | `participants.tsv` (age/sex/hand) |
| Population | Clinical intracranial-recording population, collected at clinical sites (Hospital of the University of Pennsylvania, Mayo Clinic, NIH NINDS per acknowledgements). README does **not** state a diagnosis explicitly; epilepsy-monitoring population is inferred from iEEG + clinical sites. | `README`; `dataset_description.json` Acknowledgements |
| Documented subject exclusions | **None documented** (all 20 participants in `participants.tsv`; no exclusion note in README/CHANGES) | `participants.tsv`, `README`, `CHANGES` |
| Modality | **iEEG** (intracranial: ECoG grid/strip + SEEG depth electrodes) + **behavioral events**. No audio files (vocal recall is annotated only), no other imaging. | `README`; BIDS tree (`ieeg/`, `beh/`); S3 listing |
| Task name (BIDS) | `task-PAL2` (PAL1 = non-stimulation sibling ds005059) | BIDS filenames; `README` |
| Paradigm | Paired-associates memory: per list — (1) **encoding**: 6 visually presented word pairs, 4000 ms each + 1000 ms ISI; (2) **distractor**: 6 arithmetic problems (X+Y+Z=?); (3) **cued recall**: one randomly chosen word of each pair shown as cue, participant **vocally recalls** the other word, 5000 ms per cue, all 6 pairs tested in random order. **25 lists/session** + 1 practice list (list −1). | `README`; verified in `events.tsv` (sub-R1003P/ses-0) |
| Stimuli | 250 concrete English 3-letter nouns (`stimuli/wordpools/wordpool_EN.txt`, fetched); a Spanish wordpool (`wordpool_SP.txt`) also ships. Events reference `wordpool_EN.txt`. | S3 `wordpool_EN.txt`; `events.tsv` `stim_file` column |
| Intervention (X) | **Open-loop electrical stimulation of a single electrode (lead)** located in the **hippocampus or entorhinal cortex**, delivered **at encoding** (3 of 6 word-pairs, alternating) **or at retrieval** (3 of 6 recall cues, alternating). No stimulation during the distractor. Stimulation starts **200 ms before** pair/cue onset, lasts **4.6 s**, ends **400 ms after** offset. One electrode per subject, constant across the session; parameters (anode/cathode labels, amplitude, pulse freq, pulse width, pulse count) are logged per event. | `README`; `events.tsv` `STIM_ON` rows + `stim_*` fields; `electrodes.tsv` |
| Stimulation example (R1003P) | Anode `DA1` / cathode `DA2` — left hippocampal **depth** contacts, `das.region = CA3` (MNI −17.8, −11.1, −14.2 / −22.1, −10.3, −14.6). amplitude=1500.0, pulse_freq=50 Hz, n_pulses=230, pulse_width=300 µs, stim_duration=4600 ms (50 Hz × 4.6 s = 230 ✓). **Unit flag:** sidecar says "amplitude (in milliamperes)" but 1500.0 mA is physiologically implausible; the value is consistent with **µA** (1.5 mA). Verify with authors. | `events.tsv` STIM_ON rows; `beh.json`/`events.json` sidecar; `electrodes.tsv` |
| Randomization unit | **List** (within subject, within session) — which of the 25 lists is a stimulation list, and whether it is encoding-stim or retrieval-stim | `README` |
| Randomization scheme | 20 of 25 lists **randomly assigned** as stimulation lists: **10 encoding-stim, 10 retrieval-stim**; **5 lists no stimulation**; **no list has both**. Within stimulation lists, stimulation falls on **alternating** pairs/cues (3 of 6); **half of stimulation lists start stim-on, half stim-off** (phase randomized). | `README`; pattern verified in data (R1003P/ses-0 lists 1–8: none, enc, ret, enc, none, ret, enc, enc — non-systematic) |
| Genuinely random? | Yes, per dataset documentation (random list assignment + random alternating phase). Fixed 10/10/5 quota = randomized block design, which does not break identifiability. Minor ambiguity: README does not explicitly state the 10-enc/10-ret split itself is random (only that 20/25 lists are randomly chosen as stimulation lists). | `README` |
| Trial structure (verified order) | `SESS_START` → practice (`START`→`PROB`×4→`STOP`, list −1) → per list: `ENCODING_START` → 6×(`STUDY_ORIENT` 250 ms + `STUDY_PAIR` 4000 ms [+ `STIM_ON` 4600 ms on alternating pairs]) → `START` → `MATH_START` → `PROB`×6 → `STOP` → `MATH_END` → `TEST_START` → 6×(`TEST_ORIENT` 250 ms + `TEST_PROBE` 4000 ms + `REC_START` 5000 ms window + `REC_EVENT` + `REC_END` [+ `STIM_ON` on alternating cues]) → next list | `events.tsv` (sub-R1003P/ses-0, lists 1–8 read directly) |
| Intervention timing | Encoding-stim: X during pair presentation, **strictly before** that pair's recall test (minutes later, same list). Retrieval-stim: X **concurrent with** the recall attempt (starts 200 ms pre-cue, 4.6 s over a 5 s recall window). | `README`; `events.tsv` onsets |
| Outcome (Y) | **Vocal cued recall of the paired-associate word**: `correct` (0/1), `resp_word` (recalled word; `<>` = vocalization without a word), `response_time` (s from recall onset to vocalization). | `events.json` sidecar descriptions; `events.tsv` |
| Outcome timing vs X | For encoding-stim pairs: Y (test) is **strictly after** X (stimulation during encoding). For retrieval-stim cues: Y is **concurrent with** X. | `events.tsv` |
| Behavioral labels | Recall accuracy (`correct`), response word (`resp_word`), response latency (`response_time`), probe word (`probe_word`), serial position (`serialpos`), probe position (`probepos`), math problem (`test` = [X,Y,Z]) and participant answer (`answer`). **No error-type taxonomy** (e.g., intrusion vs probe-repetition) — `resp_word` is free text. Pair-level outcome is **pre-labeled on the encoding event**: `STUDY_PAIR` rows carry `correct` (was this pair recalled at test) and `resp_word` (word said at test) — verified against the corresponding `REC_EVENT` rows. | `events.json` sidecar; `events.tsv` cross-check (e.g., list 1: OWL–STEAK `STUDY_PAIR` correct=1/resp STEAK matches `REC_EVENT` STEAK/correct=1) |
| Event annotations (events.tsv fields) | `onset, duration, sample, trial_type, response_time, stim_file, study_1, study_2, serialpos, probepos, probe_word, resp_word, correct, list, test, answer, stimulation, stim_list, stim_duration, anode_label, cathode_label, amplitude, pulse_freq, n_pulses, pulse_width, experiment, session, subject` (29 columns). `trial_type` levels: `SESS_START, START, PROB, STOP, ENCODING_START, STUDY_ORIENT, STUDY_PAIR, MATH_START, MATH_END, TEST_START, TEST_ORIENT, TEST_PROBE, REC_START, REC_END, REC_EVENT, STIM_ON`. `stim_list` ∈ {0,1} (1 = list has stimulation at encoding or retrieval); `stimulation` ∈ {0,1} (event occurs during stimulation). | `events.tsv` header (fetched); `events.json` sidecar (fetched) |
| Semantic / cognitive labels | Recalled word and correctness **are labeled** (`resp_word`, `correct`). **No word-category / semantic annotation** is provided (words are concrete nouns from a fixed pool). | `events.tsv`; `wordpool_EN.txt` |
| iEEG acquisition | **500 Hz** sampling (sidecar `SamplingFrequency`), continuous recording (~2462 s for R1003P/ses-0), EDF format. **Monopolar** files (typically mastoid-referenced — **must be re-referenced**) and **bipolar** files (paired scheme per `acq-bipolar_channels.tsv`). Channel counts vary by subject (R1003P: 92 ECoG + 8 SEEG = 100). Hardware: Blackrock (native 250 nV) and Medtronic (native 0.1 µV) systems, **scaled to V** by authors. `ElectricalStimulation: true` in sidecar. Power line 60 Hz. | `acq-monopolar_ieeg.json` / `acq-bipolar_ieeg.json` sidecars (fetched); `README` |
| Electrode locations | Per-subject unique montage; `electrodes.tsv` columns: `name, x, y, z` (MNI152NLin6ASym), `size, group, hemisphere, type` (grid/strip/depth), `tal.x/y/z` (Talairach), `ind.region, das.region, stein.region` (region annotations; some `n/a`). Stimulated contacts identified in events (e.g., R1003P DA1/DA2 = left hippocampal depth, CA3). | `electrodes.tsv` (fetched, R1003P/ses-0); `README` |
| Data size | **Total ≈ 26.34 GB** (28,279,607,571 bytes, 370 files). EDF: 51 files = 26.33 GB (26 monopolar + 25 bipolar; R1074M/ses-0 has no bipolar file). Per-session EDFs ~235–484 MB each. Behavioral/events text: 26 `beh.tsv` (102–189 KB each, 3.78 MB total) + 26 identical `events.tsv` (3.78 MB) + 52 sidecar JSONs (104 KB) + 26 `electrodes.tsv` (~10 KB each) + 26×2 `channels.tsv` (~9 KB each). | S3 bucket listing (all 370 objects, sizes parsed) |
| Derivatives | **None.** Raw only; no derivatives directory in S3 or GitHub mirror. | S3 listing; GitHub tree |
| Associated publication | **No primary journal paper for ds005494 is indexed** in PubMed, OpenAlex, or bioRxiv as of 2026-09-17 (searched by authors, title, and terms). Closest related works: (1) Rizzuto, Herrema, et al. (2025) "A wireless, 60-channel, AI-enabled neurostimulation platform", *Brain Stimulation* 19(1):103013, doi:10.1016/j.brs.2025.103013 — the stimulation hardware/platform (Kahana lab / Nia Therapeutics); (2) OSF preprints by Herrema (2024): "First Recall Costs and Benefits" (doi:10.31234/osf.io/sm3fw) and "Phonological Similarity and Recall Dynamics" (doi:10.31234/osf.io/fytq6_v1) — behavioral analyses of the same PAL paradigm family. **No published causal analysis of this stimulation dataset was found** — CM-7 would be the first. | PubMed E-utilities; OpenAlex author works (A5107494647); bioRxiv search |
| Sibling datasets (same program) | ds005059 (PAL1, no stimulation), ds005489 (free recall + open-loop stim at encoding), ds005491 (categorized free recall + open-loop stim at encoding), ds005523 (spatial memory + open-loop stim at encoding), ds005557/5558 (closed-loop stim at encoding) | OpenAlex author works |

---

## 2. Design and randomization

**Paradigm.** A within-subject, list-based paired-associates memory task (BIDS task `PAL2`). Each session contains 25 lists (plus one practice list). Each list: 6 word pairs encoded (4 s each, 1 s ISI) → 6 arithmetic distractor problems → cued recall of all 6 pairs (one word of each pair shown as cue; participant vocally produces the other; 5 s per cue; test order randomized).

**Intervention (X).** Open-loop biphasic electrical stimulation of a single intracranial electrode (lead) in the hippocampus or entorhinal cortex, with adjacent contacts as anode/cathode. Stimulation is delivered to **alternating** items: on encoding-stim lists, 3 of the 6 word-pair presentations are stimulated; on retrieval-stim lists, 3 of the 6 recall cues are stimulated. Each stimulation train: onset 200 ms before item onset, 4.6 s duration (ends 400 ms after item offset). Parameters (amplitude, 50 Hz pulse frequency, 300 µs pulse width, 230 pulses) are fixed within a subject and logged per event (`STIM_ON` rows with `anode_label`, `cathode_label`, `amplitude`, `pulse_freq`, `n_pulses`, `pulse_width`, `stim_duration`).

**Randomization logic.**
- **Unit of randomization: the list** (within subject, within session).
- 20 of the 25 lists are randomly designated as stimulation lists: 10 receive stimulation at encoding, 10 at retrieval; 5 receive no stimulation; no list receives both.
- Within a stimulation list, the **phase** of the alternating stimulation (which of the two alternating positions is stimulated) is randomized: half of stimulation lists start stim-on, half start stim-off.
- The probe (which word of a pair is cued) is randomized per pair; test order is randomized per list.
- This is a randomized block design with fixed quotas (10/10/5), which preserves identifiability.
- Verified in data (R1003P/ses-0, lists 1–8): list 1 no-stim, 2 enc-stim, 3 ret-stim, 4 enc-stim, 5 no-stim, 6 ret-stim, 7 enc-stim (phase: stim on pairs 2/4/6), 8 enc-stim (phase: stim on pairs 1/3/5) — consistent with random list assignment and random phase.

**Why this supports causal inference.** The same subject, same electrode, same stimulation parameters, same session, same list are shared by stimulated and non-stimulated items. The only systematic difference between a stimulated pair and its neighbors is the stimulation train itself. This yields two clean contrasts:
1. **Pair-level, within encoding-stim lists:** stimulated pair (X=1) vs non-stimulated pair (X=0) → recall of that pair at test.
2. **List-level:** encoding-stim lists (X=1) vs no-stim lists (X=0) → recall of list items.

---

## 3. Identifiability (the `P(Y_future | do(X))` question)

**Cleanest identifiable contrast: encoding stimulation (X=1) vs no stimulation (X=0) → subsequent cued recall (Y).**
- X (stimulation during the 4 s pair presentation, 4.6 s train) **strictly precedes** Y (cued recall of that pair at test, ~1–2 min later in the same list). Verified from event onsets.
- Randomization at the list level (and pair level within lists) is within-subject, so subject-level confounds (montage, electrode site, pathology, baseline memory) are differenced out.
- The pair-level contrast (stimulated vs non-stimulated pairs within the same encoding-stim list) is the tightest: same list, same subject, same session, same electrode, same parameters; only the stimulation differs.
- The `STUDY_PAIR` rows already carry the pre-labeled pair outcome (`correct`, `resp_word`), so the (X, Y) pairs can be constructed directly from `events.tsv`.

**Is the randomization at a level that supports this?** Yes. List-level within-subject randomization (plus randomized alternating phase) is exactly the right unit: it randomizes the treatment across lists while holding subject, electrode, session, and parameters constant. The estimand is a within-subject average treatment effect aggregated across subjects.

**Verdict: CONDITIONALLY IDENTIFIABLE.** `P(Y | do(X))` for the contrast "open-loop stimulation of the targeted hippocampal/entorhinal electrode at encoding → subsequent cued recall of the stimulated pairs" is identifiable as an **average causal effect**, under these assumptions:
1. **Randomization as documented was actually executed** (list assignment 10/10/5, alternating phase 50/50). No evidence of implementation bias found in the data (list assignments are non-systematic across lists and subjects).
2. **Estimand is site-specific:** `do(X)` means "deliver the documented open-loop train to *this subject's targeted electrode*." Because electrode location (hippocampal subfield CA1/CA3/CA4, entorhinal cortex, hemisphere, depth vs grid) varies across subjects, the estimand is "the average effect of stimulating the targeted electrode," not "the effect of hippocampal stimulation" in general.
3. **Nested structure handled:** pairs nested in lists, lists in sessions, sessions in subjects. Inference must use the list (or pair-within-list) as the effective unit with subject/session random effects; trial-level n (≈780 stim pairs vs ≈780 non-stim pairs per 260 encoding-stim lists + 130 no-stim lists) does not equal effective n.
4. **No unmeasured time-varying confounding of list assignment** — protected by randomization, but carryover (arousal/state changes induced by stimulation persisting into subsequent lists) is a realistic threat; list position should be modeled.
5. **No sham condition:** the control is "no stimulation at all," not sham stimulation. The contrast identifies the effect of stimulation-on vs off, but cannot separate the neural effect of the train from non-specific effects of being on a stimulation list (expectation, arousal, micro-seizure induction).

**The retrieval-stimulation contrast is NOT a "future state" contrast.** On retrieval-stim lists, X (4.6 s train starting 200 ms pre-cue) is **concurrent with** Y (the 5 s recall window). It can be analyzed as a concurrent manipulation of the retrieval process (identifiable under the same randomization assumptions), but it does not support `P(Y_future | do(X))` in the CM-7 sense.

**Top 3 threats to identifiability:**
1. **Neural, not cognitive, intervention.** `do(X)` is "inject current into electrode E." The causal effect is confounded with electrode site (subfield, hemisphere, depth vs grid, proximity to epileptogenic tissue) and with the biophysics of the train. The estimand is electrode-specific; cross-subject pooling assumes the targeted sites are functionally comparable (hippocampus/entorhinal), which is only approximately true (verified: R1003P target = left CA3 depth contacts).
2. **Clinical epilepsy population + no sham control.** Generalizability to healthy populations is limited; the targeted tissue is in the resection zone (stimulation may interact with the epileptogenic zone); and without sham stimulation, non-specific effects (arousal, expectation, micro-seizures) cannot be separated from the intended memory effect.
3. **Nested/clustered design with sequential carryover.** Trials are nested in lists, lists in sessions, sessions in subjects; lists are run sequentially within a session, so stimulation on one list could alter the state (arousal, attention, seizure risk) during subsequent lists. Randomization protects the average contrast, but list-order effects must be modeled, and effective sample size is at the list level (260 encoding-stim vs 130 no-stim lists; 20 subjects), not the trial level.

**Additional notes:**
- Y is a **cued** recall of a specific word — a semantic/behavioral state, but not a free/spontaneous thought state. For CM-7's "thought-state" framing this is a narrow, well-defined outcome.
- Stimulation dose cannot be varied within the dataset (fixed parameters per subject); dose–response analysis is impossible.
- The `correct` label on `STUDY_PAIR` rows is the test outcome (verified against `REC_EVENT` rows) — convenient, but it means Y is defined at the pair level, not the single-trial level.

---

## 4. Data layout for minimal acquisition

Base URL: `https://s3.amazonaws.com/openneuro.org/ds005494/`

**Minimal behavioral/events subset (≈ 8.5 MB total, no iEEG):**

| File pattern | Count | Size each | Total |
|---|---|---|---|
| `sub-{sub}/ses-{ses}/beh/sub-{sub}_ses-{ses}_task-PAL2_beh.tsv` | 26 | 102–189 KB | 3.78 MB |
| `sub-{sub}/ses-{ses}/beh/sub-{sub}_ses-{ses}_task-PAL2_beh.json` | 26 | 3,985 B | 104 KB |
| `sub-{sub}/ses-{ses}/ieeg/sub-{sub}_ses-{ses}_task-PAL2_events.tsv` | 26 | 102–189 KB (byte-identical to beh.tsv, same ETag) | 3.78 MB |
| `sub-{sub}/ses-{ses}/ieeg/sub-{sub}_ses-{ses}_task-PAL2_events.json` | 26 | 3,985 B (identical to beh.json) | 104 KB |
| `sub-{sub}/ses-{ses}/ieeg/sub-{sub}_ses-{ses}_task-PAL2_space-MNI152NLin6ASym_electrodes.tsv` | 26 | ~10 KB | ~270 KB |
| `sub-{sub}/ses-{ses}/ieeg/sub-{sub}_ses-{ses}_task-PAL2_acq-monopolar_channels.tsv` | 26 | ~3.7 KB | ~95 KB |
| `sub-{sub}/ses-{ses}/ieeg/sub-{sub}_ses-{ses}_task-PAL2_acq-bipolar_channels.tsv` | 25 | ~5.6 KB | ~140 KB |
| `participants.tsv` | 1 | 388 B | — |
| `dataset_description.json`, `CHANGES`, `README` | 3 | < 5 KB | — |

`{sub}` ∈ {R1003P, R1016M, R1028M, R1031M, R1036M, R1050M, R1060M, R1074M, R1082N, R1091N, R1095N, R1111M, R1112M, R1118N, R1121M, R1130M, R1136N, R1149N, R1162N, R1185N}
`{ses}`: R1003P {0,1}, R1016M {0,1,2}, R1031M {0,1}, R1060M {0,1}, R1111M {0,1}, **R1091N {1} only**, all others {0}.

**Large iEEG files (do NOT download for behavioral analysis):**
- `sub-{sub}/ses-{ses}/ieeg/sub-{sub}_ses-{ses}_task-PAL2_acq-monopolar_ieeg.edf` — 26 files, 235–424 MB each
- `sub-{sub}/ses-{ses}/ieeg/sub-{sub}_ses-{ses}_task-PAL2_acq-bipolar_ieeg.edf` — 25 files, 268–484 MB each (missing for R1074M/ses-0)
- All 51 EDFs together: **26.33 GB** (99.97% of the 26.34 GB dataset total)

**Example minimal download (one session):**
```
https://s3.amazonaws.com/openneuro.org/ds005494/sub-R1003P/ses-0/beh/sub-R1003P_ses-0_task-PAL2_beh.tsv
https://s3.amazonaws.com/openneuro.org/ds005494/sub-R1003P/ses-0/ieeg/sub-R1003P_ses-0_task-PAL2_events.tsv
https://s3.amazonaws.com/openneuro.org/ds005494/sub-R1003P/ses-0/ieeg/sub-R1003P_ses-0_task-PAL2_space-MNI152NLin6ASym_electrodes.tsv
```

---

## 5. Verification status

| Item | Status | How verified |
|---|---|---|
| Name, authors, license, BIDS version, funding, DatasetDOI | VERIFIED | S3 `dataset_description.json` (fetched) |
| Snapshot v1.0.1, release dates | VERIFIED | `DatasetDOI` + `CHANGES` (GitHub) + GitHub repo push date; OpenNeuro web UI/API **unreachable** from audit environment (transport errors) — not independently confirmed via OpenNeuro site |
| N=20 subjects, 26 sessions, demographics | VERIFIED | `participants.tsv` (fetched), GitHub tree (20 sub dirs), `CHANGES`, S3 listing (26 beh.tsv) |
| Paradigm, list structure, timings (4000 ms pairs, 1000 ms ISI, 5000 ms recall, 25 lists) | VERIFIED | `README` (fetched) + direct read of `events.tsv` onsets/durations (sub-R1003P/ses-0) |
| Intervention: open-loop stimulation, site, timing (200 ms pre, 4.6 s), alternating 3-of-6 | VERIFIED | `README` + `STIM_ON` rows in `events.tsv` (onset/duration/amplitude/freq/pulses/width) |
| Randomization: 20/25 lists, 10 enc / 10 ret / 5 none, no list both, random phase | VERIFIED (as documented) | `README`; list-assignment pattern in data (lists 1–8 of R1003P/ses-0) is non-systematic. The randomization procedure itself is as documented by the authors (not independently re-derivable from data) |
| events.tsv field names + meanings | VERIFIED | Header row (fetched) + `events.json` sidecar descriptions (fetched) |
| Pair outcome pre-labeled on STUDY_PAIR | VERIFIED | Cross-checked `STUDY_PAIR.correct`/`resp_word` against corresponding `REC_EVENT` rows (list 1, R1003P/ses-0) |
| iEEG: 500 Hz, monopolar+bipolar, channel counts, MNI/Talairach coords, region labels, ElectricalStimulation=true | VERIFIED | iEEG sidecar JSONs + `electrodes.tsv` (fetched, R1003P/ses-0); README notes |
| Data sizes (26.34 GB total; per-file) | VERIFIED | Full S3 bucket listing (370 objects) parsed locally |
| No derivatives | VERIFIED | S3 listing + GitHub tree (no derivatives dir) |
| Stimuli = 250 concrete English nouns | VERIFIED | `wordpool_EN.txt` (fetched from S3) |
| Associated paper | **NOT FOUND** (no primary paper indexed in PubMed/OpenAlex/bioRxiv as of 2026-09-17) | PubMed esearch/esummary, OpenAlex author works, bioRxiv search. Closest: Rizzuto et al. 2025 (Brain Stimulation, hardware platform) + 2 OSF preprints (behavioral analyses of PAL paradigm) |
| Amplitude units (mA per sidecar vs 1500.0 value) | **FLAGGED** — likely µA, not mA; verify with authors | `events.json` sidecar text vs `events.tsv` values |
| "Epilepsy patients" | INFERRED (not stated in README) | iEEG + clinical sites; README says "clinical sites" only |
| Whether the 10-enc/10-ret split is itself random | UNVERIFIED (minor) | README does not state it explicitly |
| OpenNeuro web UI / API snapshot list | UNVERIFIED (unreachable) | `api.openneuro.org` transport errors; `openneuro.org` page is JS-only |
