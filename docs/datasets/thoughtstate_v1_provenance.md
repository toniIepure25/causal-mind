# ThoughtStateV1 — Field Provenance

Module: `src/causal_mind/thought/state_v1.py`. Built on the validated CM-1 loader
(`src/causal_mind/data/ds006067.py`).

## Data available in ds006067 (validated loader)

The loader exposes, per thought event: `onset` (s), `duration` (s), `transcript`
(str). That is the **entirety** of the per-thought data. There are NO topic labels,
NO word-level timestamps, NO affect/temporality/self-relevance annotations, and NO
psychological ratings in ds006067. This is the single most important provenance fact.

## Field-by-field provenance

| Field | Provenance class | How produced | Leakage note |
|-------|------------------|--------------|--------------|
| `transcript` | **directly observed** | BIDS `events.tsv` `transcript` column | — |
| `onset` | **directly observed** | `events.tsv` `onset` (s) | — |
| `duration` | **directly observed** | `events.tsv` `duration` (s) | — |
| `offset` | derived (deterministic) | `onset + duration` | — |
| `n_words` | derived (deterministic) | `len(transcript.split())` | — |
| `n_chars` | derived (deterministic) | `len(transcript)` | — |
| `embedding` | **model inferred** | frozen `all-MiniLM-L6-v2` (384-d), pretrained, **no fitting on CM-2 text** | encoder never trained on any CM-2 transcript |
| `category` | **model inferred** | K-means (k=16) on `embedding`, **fit on TRAIN subjects only**, assigned to all | clustering fit excludes val/test subjects |

## Candidate dimensions classified as UNAVAILABLE

The following candidate dimensions are **not present** in ds006067 and are therefore
classified `unavailable` — they are NOT fabricated from model labels and are NOT used as
ground truth:

* temporality, self-relevance, episodic/past-oriented, future-oriented,
  affect/valence, goal-directedness, social content, task-relatedness.

If a later milestone wants any of these, they must be introduced as **model-inferred**
features (clearly labeled) or via a genuinely annotated dataset — never silently treated
as observed ground truth.

## Separation of observed vs learned

* The **original annotation** (transcript text + timing) is preserved verbatim in
  `ThoughtState.transcript/onset/duration` and is never overwritten.
* **Learned** fields (`embedding`, `category`) are attached separately and are always
  labeled model-inferred. Nothing in the pipeline mutates the observed fields.

## Predictive-feature policy (prospective safety)

Fields allowed as features for predicting thought `t+1`: `embedding`, `n_words`, `onset`,
`duration` (all from thoughts `<= t`). Deliberately EXCLUDED: any quantity that depends on
thought `t+1` or later (e.g., gap-to-next, boundary-to-next) — these would be future
information.
