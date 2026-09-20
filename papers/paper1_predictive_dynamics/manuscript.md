# Predicting the Future of the Thought Stream: Multi-Horizon Semantic Forecasting of Spontaneous Cognition

**Manuscript draft (Paper 1 — predictive dynamics).** Status: pre-submission draft, part of
the `cm8-prehuman-v1.0` freeze. All values are copied verbatim from the committed reports
(`reports/cm2_results.json`, `reports/cm3_results.json`). No human data beyond the public
corpus; no causal claim; no free-will claim.

---

## Abstract

Spontaneous cognition — the stream of unprompted thoughts — is difficult to predict, yet
its structure may be partly forecastable from its own recent history. We ask whether the
*semantic content* of a person's next thought, and of thoughts several steps ahead, can be
predicted from a short window of recent thought history, out-of-sample and above strong
baselines. Using a public corpus of 6,436 thought events from 118 participants (OSF
`a56rm`), we represent each thought with a frozen sentence embedding and fit a simple
ridge multi-horizon forecaster over a k≈3 history window, evaluated on a sealed,
subject-disjoint test split. The model predicts the next thought's semantics at a held-out
cosine similarity of **0.362 [95% CI 0.352, 0.372]**, above all eight baselines (strongest
0.317 [0.308, 0.325]). It also predicts *future* thoughts at every event horizon h=1..10,
with a smooth, monotonic decay of the gain over the strongest horizon-specific baseline
(+0.035 [0.025, 0.045] at h=1 to +0.004 at h=10, all 95% CIs excluding zero), implying a
semantic predictive horizon of at least ~10 thoughts (~2 minutes). The effect is modest and
the test set is small (n=17 subjects); we make no causal and no free-will claim. The
result establishes that the thought stream carries a real, finite, forecastable semantic
signal — the empirical foundation for the program's intervention work.

## 1. Introduction

The stream of spontaneous thought is a central object of cognitive science, yet it is
treated as largely unforecastable: each thought is assumed to depend on an unbounded,
idiosyncratic context. We take the opposite stance as a testable hypothesis: **the recent
past of the thought stream contains predictive information about its semantic future.** If
true, the thought stream is a *predictive* dynamical system with a finite horizon, and that
horizon becomes a natural target for intervention.

We contribute:
1. A **thought-state representation** (frozen sentence embeddings over a short history
   window) and a **simple, reproducible multi-horizon forecaster**.
2. Evidence of **next-thought** (L3) and **multi-horizon** (L5) semantic prediction,
   out-of-sample, subject-disjoint, above strong baselines, with a smooth decay of the
   gain with horizon.
3. A **Thought Predictive Horizon** (TPH) estimate: the signal persists to at least 10
   thoughts ahead (~2 minutes), a lower bound.

We are explicit about scope: the effect is modest, the test set is small, the category
(non-semantic) arm is unvalidated, and we make **no causal and no free-will claim**.

## 2. Related work

- **Thought diaries / experience sampling.** The OSF `a56rm` corpus (a think-aloud
  cognitive-diary study with concurrent fMRI) provides longitudinal, per-subject thought
  streams with semantic and affect ratings.
- **Sequence prediction over text.** n-gram, Markov, and retrieval baselines are the
  natural null models for "what comes next." We include them (B0–B7) and show the
  embedding-based transition model beats them.
- **Multi-horizon forecasting.** We follow the standard practice of evaluating each
   horizon against its own strongest baseline and reporting the gain with a confidence
   interval, rather than a single pooled accuracy.

## 3. Data and pre-processing

- **Corpus:** OSF `a56rm` thought diaries; 118 subjects, 6,436 thought events.
- **Representation:** each thought is encoded with a frozen `all-MiniLM-L6-v2` sentence
  embedding (local; no network at inference). The thought *state* is a k≈3 sliding window
  of recent embeddings (history depth saturates at k≈3).
- **Split:** **subject-disjoint** 83 (train) / 18 (val) / 17 (test), **sealed**
  (seal `67505261…`). No random row splits on temporal data; no subject appears in more
  than one split.
- **Metric:** cosine similarity between the predicted and the actual future thought
  embedding (the *semantic* arm). The *category* arm is reported as unvalidated.

## 4. Methods

- **Forecaster:** `LinearMultiHorizon` — a ridge regression (α=100) from the k≈3 history
  state to each horizon's target embedding. Fitted on the train split; horizon-specific
  heads.
- **Baselines (B0–B7):** marginal (B0), previous-state (B1), Markov (B2), n-gram (B3),
  semantic persistence/drift (B4), semantic nearest-neighbor (B5), participant history
  (B6), history retrieval (B7). For each horizon we compare against the *strongest*
  horizon-specific baseline.
- **Evaluation:** held-out test split; 95% confidence intervals by subject-level bootstrap;
  permutation null (p=0.0000) for the next-thought result; the multi-horizon result
  survives time-shuffled, transition-destroyed, and random-target nulls (p=0.0000).
- **Reproducibility:** the forecaster is frozen; a clean-room re-fit from source + data is
  bit-identical (SHA-verified). Exact commands in `docs/releases/cm8_prehuman_v1.md`.

## 5. Results

### 5.1 Next-thought prediction (L3)

The model reaches held-out semantic cosine **0.3623 [0.3523, 0.3720]**. The strongest
baseline, B0 (marginal), is **0.3167 [0.3078, 0.3250]**; the model's CI does not overlap
the baseline's. All eight baselines are beaten. Permutation null p=0.0000.

### 5.2 Multi-horizon prediction (L5)

The model beats the strongest horizon-specific baseline at **every** horizon h∈{1,2,3,4,5,6,8,10}.
Gain over the strongest baseline:

| horizon h | model | strongest baseline | gain [95% CI] |
| --- | --- | --- | --- |
| 1 | 0.3623 | B4 drift 0.3274 | +0.0349 [0.0253, 0.0445] |
| 2 | 0.3406 | B0 marginal 0.3146 | +0.0261 [0.0205, 0.0321] |
| 3 | 0.3285 | B0 marginal 0.3133 | +0.0152 [0.0091, 0.0220] |
| 4 | 0.3236 | B0 marginal 0.3122 | +0.0114 [0.0070, 0.0165] |
| 5 | 0.3210 | B0 marginal 0.3117 | +0.0093 [0.0038, 0.0148] |
| 10 | — | — | +0.0044 (CI excludes 0) |

The gain decays **smoothly and monotonically** with horizon — the expected signature of a
real, finite-horizon signal rather than an artifact. Because the gain is still significant
at the maximum tested horizon (h=10), the **Thought Predictive Horizon (TPH_semantic) is at
least ~10 thoughts (~2 minutes)**, a lower bound.

## 6. Discussion

The thought stream is a *predictive* dynamical system: its recent semantic state carries
information about its near semantic future, above strong null models, out-of-sample and
subject-disjoint. The smooth decay of the gain with horizon is the key qualitative result:
it is the pattern a real, finite-horizon signal produces, and it is what makes the
predictive horizon a meaningful, intervention-relevant quantity. We emphasize the modest
size of the effect and the small test set; the contribution is the *establishment* of the
signal and its horizon, not its magnitude.

## 7. Limitations

- **Modest effect; small test set** (n=17 subjects). The CIs are tight but the absolute
  gain is small.
- **Semantic arm only.** The category (non-semantic) arm is unvalidated.
- **Single corpus.** Generalization across corporases/tasks is not established.
- **No causal claim.** Prediction is not intervention; the causal question is addressed
  separately (Paper 2 / the CM-8 experiment).
- **No free-will claim.** A forecastable thought stream is not a claim about free will.

## 8. Conclusion

Spontaneous thought is partly forecastable: a simple, reproducible model predicts the next
thought and future thoughts at every horizon up to ten, with a smooth decay of the gain and
a semantic predictive horizon of at least ~2 minutes. This establishes the empirical
foundation for the program's intervention work and is reported here with its exact values,
baselines, nulls, and limitations.

## References

(To be completed at submission. Cite: OSF `a56rm` corpus; `all-MiniLM-L6-v2`; the
subject-disjoint split protocol; the multi-horizon evaluation protocol. All internal
artifacts are cited by SHA in `docs/claims/evidence_matrix.md`.)
