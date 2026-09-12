# CM-2 — THOUGHT STATE + NEXT (final report)

**Decision: `CM2_PASS`** (modest but genuine, significant, reproducible effect)

Past thought history contains genuine out-of-sample information about the next
thought, above strong trivial / semantic / participant-history baselines, under
strict subject-disjoint prospective evaluation. No fMRI in this result.

## PROVENANCE

Dual-source dataset model (recorded in manifest + provenance docs):
- **MRI source:** OpenNeuro `ds006067 v2.0.0` (neuroimaging; not used in CM-2).
- **Behavioral source:** OSF project `a56rm` (transcripts, timestamps, ratings,
  questionnaires, code). Raw files immutable under `data/raw/osf/...`;
  normalized derived thought events under `data/derived/thought_events/...`.
- Field provenance (`thought/state_v1.py`): transcript/onset/duration/topic/
  observed_category = **directly observed**; offset/n_words/n_chars = derived;
  embedding/category = **model inferred**; 14 psychological ratings =
  **model inferred (GPT)**, human-validated on an 18-subject subset. Model-
  inferred fields are never treated as ground truth.

## THOUGHT STATE V1

The "thought" unit = sentences grouped by the OSF `thoughtID` column
(sub-001: 64 sentences → 28 thoughts). Features: frozen MiniLM text embedding
(384-d, primary signal), n_words, onset, duration, topic, observed_category,
and 14 GPT-rated dimensions (not in the primary result).

## DATA

- 118 subjects, 6436 thoughts (OSF sentence-level, all 118 have transcripts +
  GPT ratings; 102 have word-level; 18 have human-validated ratings).
- Cohort integrity: all 10 checks PASS (subject count, no duplicate IDs/events,
  monotonic timestamps, valid intervals, no missing text, event order =
  temporal order, no cross-subject contamination of substantive text,
  annotation provenance).
- Split: subject-disjoint **83/18/17** (train/val/test), sealed
  `675052618750ea7f780c566230c47baabb983955b28bc35f49fe58d6c0408668` before any
  test metric. Protocol amendment 001 documents the OSF source change (cohort
  unchanged vs. the original sealed protocol).

## BASELINES (test, k=1; semantic cosine [95% subject-bootstrap CI])

| Baseline | semantic | category |
|---|---|---|
| B0_marginal | 0.3167 [0.3078, 0.3250] | 0.1464 |
| B1_previous_state | 0.2717 [0.2550, 0.2883] | 0.2566 |
| **B2_markov (strongest)** | **0.3265 [0.3149, 0.3381]** | 0.2566 |
| B3_ngram | 0.3265 [0.3149, 0.3381] | 0.2566 |
| B4_semantic_persistence | 0.2796 [0.2630, 0.2961] | 0.2566 |
| B5_semantic_nn | 0.2972 [0.2871, 0.3078] | 0.2257 |
| B6_participant_history | 0.2717 [0.2550, 0.2883] | 0.2566 |
| B7_history_retrieval | 0.2564 [0.2462, 0.2674] | 0.2566 |

## BEST MODEL

`LinearTransition` (ridge) over a k=3 window of history embeddings → next
embedding. Selected on VAL (k=3, alpha=100, val 0.3493); final eval on TEST.
**Test semantic: 0.3623 [0.3523, 0.3720].**

**GRU capacity check:** a small GRU (k=3, 111k params, 30 epochs) scores
**0.3357 [0.3236, 0.3483]** — *worse* than the linear model. No non-linear
headroom; the linear transition is the right capacity for this data size
(consistent with the history-depth curve saturating at k≈3).

## PRIMARY RESULTS

- The model beats **every** baseline. vs. strongest (B2/B3 markov):
  0.3623 vs 0.3265, **non-overlapping CIs** (0.3523 > 0.3381), Δ ≈ 0.036.
- Even at matched **k=1** the model (0.3531) beats the best baseline (0.3265),
  so the advantage is not an artifact of the longer window.
- Permutation null: observed 0.3635 vs null 0.2958, **p = 0.0000** — the effect
  is not an embedding-structure artifact.

## HISTORY DEPTH (A5)

k=1: 0.3531 · k=2: 0.3617 · **k=3: 0.3623** · k=5: 0.3597 · k=8: 0.3551.
Performance saturates at k≈3 and declines with longer windows (overfitting).
Added history (A2): k=3 (0.3623) > k=1 (0.3531).

## CROSS-SUBJECT (A4)

n=17 test subjects; per-subject mean semantic 0.3623 [0.3523, 0.3720]. The
effect is not driven by a single subject.

## NEGATIVE CONTROLS

- **Immediate (A1):** B1_previous_state (0.2717) < B0_marginal (0.3167) — the
  immediate previous thought is a *worse* predictor than the marginal (thoughts
  shift topic). The model must overcome this inertia, which it does.
- **Permutation (A6):** p = 0.0000 (above).
- **B2 == B3 at k=1** is expected (n-gram term inactive at k=1), not a bug.

## RED TEAM

Independent red-team review (`docs/review/cm2_redteam_review.md`): **GO**.
Leakage audit PASS (split disjoint, train-only fitting, frozen encoder,
prospective guard). Baselines strong and correct. Metrics correct (subject-level
CIs, valid null). **Reproduced from a clean process** — all key numbers match
exactly (main 0.3623, B2 0.3265, p=0.0000).

## CLAIMS AUTHORIZED / NOT

**Authorized (level 3–4):**
- Past thought history (a short k≈3 window of text embeddings) predicts the next
  thought's semantics above strong trivial/semantic/participant-history
  baselines, out-of-sample, subject-disjoint, prospective. Effect is real
  (permutation p=0.0000) but **modest** (Δ≈0.036 over the best baseline).

**NOT authorized:**
- Any causal claim (this is associative prediction, not intervention).
- Categorical prediction (the model predicts embeddings only; A3 category arm
  is NaN — unvalidated).
- Any claim relying on the GPT-rated psychological dimensions (model-inferred;
  not in the primary result).
- Neural / fMRI claims (out of scope for CM-2; CM-5).

## DECISION

`CM2_PASS` — the CM-2 hypothesis is supported with a modest, significant,
reproducible effect. The category arm and the GPT-rating features remain open
for iteration.

## NEXT STEP

CM-2 iteration (optional, `CM2_ITERATE` track): (a) add a categorical head to
the transition model to validate the category arm; (b) test whether the 14
GPT-rated dimensions (with the 18-subject human validation) add predictive value
beyond text; (c) a small GRU to check for non-linear headroom beyond the linear
transition. Then proceed to **CM-5** (neural), which requires OpenNeuro (S3
outage no longer a CM-2 blocker; keep the retry alive for CM-5).
