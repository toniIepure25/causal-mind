# ThoughtStateV1 — Field Provenance

Module: `src/causal_mind/thought/state_v1.py`. Loader:
`src/causal_mind/data/osf_a56rm.py` (OSF behavioral source).

## Dual-source dataset model

ds006067 is published across two authoritative sources:

| Modality | Source |
|---|---|
| Neuroimaging (MRI) | OpenNeuro `ds006067 v2.0.0` |
| Behavioral (transcripts, timestamps, ratings, questionnaires, code) | OSF project `a56rm` |

**The behavioral data used by CM-2 comes from OSF `a56rm`, not OpenNeuro.**
Raw OSF files are preserved immutable under `data/raw/osf/...` (never renamed
into fake BIDS `events.tsv`); the normalized derived thought events live under
`data/derived/thought_events/<sub>_thoughts.tsv`.

## The "thought" unit

OSF sentence-level transcripts carry a `thoughtID` column that groups
consecutive sentences into **thoughts** (the next-thought unit). sub-001:
64 sentences → 28 thoughts; sub-005: 147 → 70. Each thought's `topic` (the
prompt) and `category` are consistent within the group.

## Field-by-field provenance

| Field | Provenance class | How produced | Leakage note |
|-------|------------------|--------------|--------------|
| `transcript` | **directly observed** | OSF sentence-level `Transcribed Sentence`, concatenated within a `thoughtID` | — |
| `onset` | **directly observed** | min sentence `Start Time` (s, relative to first functional volume) | — |
| `duration` | **directly observed** | max `End Time` − min `Start Time` | — |
| `topic` | **directly observed** | OSF `topic` (the prompt the subject thought about) | — |
| `observed_category` | **directly observed** | OSF `category` (1-5) | — |
| `offset` | derived (deterministic) | `onset + duration` | — |
| `n_words` | derived (deterministic) | `len(transcript.split())` | — |
| `n_chars` | derived (deterministic) | `len(transcript)` | — |
| `embedding` | **model inferred** | frozen MiniLM (`all-MiniLM-L6-v2`, 384-d) on transcript; no fitting | — |
| `category` | **model inferred** | K-means on embedding, fit on TRAIN subjects only | leakage-safe |
| 14 ratings (`emotional_intensity`, `joy`, `sadness`, `fear`, `anger`, `disgust`, `surprise`, `anxiety`, `vision`, `audition`, `olfaction`, `gustation`, `somatosensation`, `interoception`) | **model inferred (GPT)** | GPT-generated sentence-level ratings, mean-aggregated to the thought | see below |

### Rating provenance (important)

The 14 psychological ratings are **model-inferred (GPT-generated)** for all
118 subjects. They are **NOT ground truth.** An 18-subject subset has
independent human ratings (4 raters) that cross-check the GPT ratings; that
subset is a *validation* cohort for rating provenance, not the main analysis
cohort. The GPT ratings are kept separate from the directly-observed
transcript and are never treated as ground truth.

## What is still unavailable

Even with OSF, there are no ground-truth annotations for: fine-grained
temporality (past/present/future), self-relevance, goal-directedness, or
episodic-semantic distinction. Those remain out of scope for CM-2.

## Coverage (verified by audit, not assumed)

* sentence-level transcripts: 118/118
* word-level timestamps: 102/118
* GPT ratings: 118/118
* human-validated ratings: 18/118 (4 raters)
