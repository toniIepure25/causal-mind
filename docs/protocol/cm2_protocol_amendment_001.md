# CM-2 Protocol Amendment 001 — OSF behavioral source

**Status:** PROSPECTIVE (recorded before any decisive CM-2 outcome)
**Supersedes:** the data-source assumptions in `cm2_frozen_protocol.md`
**Seal (amended):** `675052618750ea7f780c566230c47baabb983955b28bc35f49fe58d6c0408668`

## 1. Discrepancy (documented before outcomes)

The original sealed CM-2 protocol assumed the behavioral data came from
OpenNeuro `ds006067` `events.tsv` (transcript + onset/duration only, no
annotations). The official ds006067 publication splits the release across two
authoritative sources:

| Modality | Authoritative source |
|---|---|
| Neuroimaging (MRI) | OpenNeuro `ds006067 v2.0.0` |
| Behavioral (transcripts, timestamps, ratings, questionnaires, code) | OSF project `a56rm` ("Think aloud behavioral data") |

OpenNeuro's S3 was also in an outage at the time of the original protocol, so
the `events.tsv` path was never the operative behavioral source. **OSF `a56rm`
is now the authoritative behavioral source for CM-2.**

## 2. What changed vs. the original protocol

1. **Data source:** behavioral events now come from OSF `a56rm`
   (`data/transcripts_and_timestamps/sentence_level/sub-<ID>_transcripts.xlsx`),
   normalized to `data/derived/thought_events/<sub>_thoughts.tsv`. The raw OSF
   files are preserved immutable under `data/raw/osf/...` (never renamed into
   fake BIDS `events.tsv`).
2. **The "thought" unit:** sentences are grouped by the OSF `thoughtID`
   column into thoughts (the next-thought unit). sub-001: 64 sentences → 28
   thoughts; sub-005: 147 → 70.
3. **Ontology fields added** (all provenance-tagged in
   `thought/state_v1.py`):
   * `topic` (directly observed — the prompt the subject thought about)
   * `observed_category` (directly observed — OSF category 1-5)
   * 14 psychological ratings (model-inferred, GPT-generated): 8 emotion
     (emotional_intensity, joy, sadness, fear, anger, disgust, surprise,
     anxiety) + 6 sensory/modal (vision, audition, olfaction, gustation,
     somatosensation, interoception).
4. **Primary signal unchanged:** the CM-2 primary result is still the frozen
   MiniLM text embedding of the thought transcript. The new fields are
   provenance-tagged and available, but the headline comparison (history vs.
   baselines) is text-based, keeping it comparable to the original protocol.

## 3. Cohort — UNCHANGED

Verified: the OpenNeuro `participants.tsv` subject set and the OSF
sentence-level subject set are **identical** (118 subjects, intersection 118,
no OpenNeuro-only, no OSF-only). The eligible cohort is therefore the same 118
subjects; only the behavioral data source changed.

Behavioral artifact coverage (verified by audit, not assumed):
* sentence-level transcripts: **118/118**
* word-level timestamps: **102/118**
* GPT-generated ratings: **118/118**
* human-validated ratings (4 raters): **18/118** (a validation subset used to
  cross-check the GPT ratings, not the main analysis cohort)

## 4. Re-sealed split (recorded before outcomes)

* Rule: subject-disjoint, deterministic, seeded (`seed=20260911`), sorted;
  70/15/15 → **train/val/test = 83/18/17**.
* No thought-level row split anywhere.
* **SEAL:** `675052618750ea7f780c566230c47baabb983955b28bc35f49fe58d6c0408668`
  persisted to `data/manifests/cm2_split_seal.json`. The evaluation runner
  verifies this seal before reporting any test metric.

## 5. Metrics, controls, gates — UNCHANGED

Primary metric (mean cosine of predicted vs. actual next-thought embedding),
subject-level bootstrap CIs, the six CM-2F analyses, the permutation null, and
closure gates B1-B5 are all as in `cm2_frozen_protocol.md`.
