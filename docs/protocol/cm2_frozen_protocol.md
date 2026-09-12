# CM-2 Frozen Evaluation Protocol

Module: `src/causal_mind/eval/protocol.py`. **Frozen and sealed before any comparative
result is inspected.**

## Split

* **Subject-disjoint** train/val/test. Subjects (never thoughts) are shuffled by a seeded
  RNG (`seed=20260911`) and cut into **70% train / 15% val / 15% test**.
* With 118 subjects this is ~82 train / ~18 val / ~18 test (exact counts fixed by the
  seed once the full subject list is available).
* **No random thought-level row split anywhere.** A thought and all its neighbors stay
  with their subject.
* **Seal**: the split is hashed (SHA-256 over `{seed, n_subjects, split}`) and persisted to
  `data/manifests/cm2_split_seal.json` BEFORE any model is fit or any test metric computed.
  `verify_seal()` re-checks the hash so the split cannot be quietly changed.

## Model selection vs final evaluation (nested separation)

* **Train** subjects: fit all transforms (TF-IDF vectorizer, K-means categories) and all
  models.
* **Val** subjects: model selection (e.g., choose history window k, ridge alpha, GRU
  epochs) — the ONLY place hyperparameters are tuned.
* **Test** subjects: final evaluation, touched exactly once, after the model is fixed.

## Primary metrics (defined per target, pre-results)

* **Semantic target** (next thought's frozen embedding):
  * primary = mean **cosine similarity** (predicted vs actual);
  * secondary = **retrieval rank / top-1 / top-5** against a candidate pool of valid
    next-thoughts (robust to embedding scale).
* **Categorical target** (coarse topic, model-inferred): **accuracy** + **log-loss**
  (calibration).
* **Timing** (secondary, not the primary claim): onset/duration regression (MAE), reported
  but not used to close the gate.

## Uncertainty

* **Subject-level bootstrap**: resample test subjects (with replacement), recompute the
  per-subject mean metric, 2000 resamples → 95% CI. (Resampling subjects, not thoughts,
  respects the subject-disjoint structure.)
* **Permutation null**: pair each test history with a RANDOM target (preserves the
  marginal distribution of next-states, destroys the specific temporal correspondence).
  200 permutations → null distribution + one-sided p-value. A real prospective effect must
  sit above this null.
* **Effect size**: delta over the **strongest** baseline (typically B4/B5), not just over
  chance (B0).

## Gate logic (pre-committed)

* **B3 (non-trivial next signal)**: at least one meaningful future dimension is predicted
  above the frozen strong baselines with a valid CI and a significant permutation null.
* If B3 fails: **do not loosen the gate** — characterize the null (which dimensions /
  horizons fail) and report `CM2_NULL` or `CM2_ITERATE`.
