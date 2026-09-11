"""Critical analyses (CM-2F).

Answers the six required questions, each with subject-level bootstrap CIs, a
permutation null, and effect sizes:
  1. Immediate predictability      -- does T_t predict T_{t+1}?
  2. Added historical information  -- does T_{t-k:t} beat T_t only?
  3. Semantic vs categorical       -- which dimensions are predictable?
  4. Cross-subject generalization  -- per-test-subject distribution
  5. History-depth curve           -- performance vs history length k
  6. Null / permutation control    -- destroy temporal correspondence

A unified predictor returns a ``Prediction`` (embedding and/or category).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from causal_mind.eval.protocol import bootstrap_ci, category_accuracy, cosine
from causal_mind.forecast.baselines import Prediction, TrainCorpus
from causal_mind.thought.prospective import Sample, build_prospective_samples
from causal_mind.thought.state_v1 import ThoughtState


def model_as_predictor(model):
    def predict(sample: Sample, states: list[ThoughtState], corpus: TrainCorpus) -> Prediction:
        return Prediction(embedding=model.predict(sample, states))
    return predict


@dataclass
class SubjectScores:
    semantic: list[float] = field(default_factory=list)   # per test subject: mean cosine
    categorical: list[float] = field(default_factory=list)  # per test subject: mean accuracy


def eval_predictor(predict, states_by_subject: dict[str, list[ThoughtState]],
                   test_subjects: list[str], k: int, corpus: TrainCorpus) -> SubjectScores:
    """Evaluate one predictor on the test subjects; return per-subject scores."""
    sem, cat = [], []
    for sub in test_subjects:
        st = states_by_subject[sub]
        samples = build_prospective_samples(st, k=k)
        coses, cats = [], []
        for s in samples:
            pred = predict(s, st, corpus)
            actual = st[s.target_index]
            if pred.embedding is not None:
                coses.append(cosine(pred.embedding, actual.embedding))
            if pred.category is not None and actual.category is not None:
                cats.append(category_accuracy(pred.category, actual.category))
        if coses:
            sem.append(float(np.mean(coses)))
        if cats:
            cat.append(float(np.mean(cats)))
    return SubjectScores(semantic=sem, categorical=cat)


def _mean_ci(scores: list[float], seed: int = 0) -> tuple[float, float, float]:
    return bootstrap_ci(np.asarray(scores), n_boot=2000, seed=seed)


# --------------------------------------------------------------------------- #
# 1. Immediate predictability
# --------------------------------------------------------------------------- #
def immediate_predictability(b0, b1, states_by_subject, test_subjects, k, corpus, seed=0):
    m0 = eval_predictor(b0, states_by_subject, test_subjects, k, corpus)
    m1 = eval_predictor(b1, states_by_subject, test_subjects, k, corpus)
    return {
        "B0_marginal": _mean_ci(m0.semantic, seed),
        "B1_previous_state": _mean_ci(m1.semantic, seed),
        "delta": _mean_ci(np.asarray(m1.semantic) - np.asarray(m0.semantic), seed),
        "note": "B1 (T_t only) vs B0 (marginal): semantic inertia / immediate predictability",
    }


# --------------------------------------------------------------------------- #
# 2. Added historical information  (k>1 vs k=1)
# --------------------------------------------------------------------------- #
def added_history(fit_fn, states_by_subject, test_subjects, corpus, ks=(1, 2, 3, 5), seed=0):
    """``fit_fn(k)`` returns a predictor fit for history window k (on train)."""
    out = {}
    for k in ks:
        m = eval_predictor(fit_fn(k), states_by_subject, test_subjects, k, corpus)
        out[f"k={k}"] = _mean_ci(m.semantic, seed)
    return out


# --------------------------------------------------------------------------- #
# 3. Semantic vs categorical
# --------------------------------------------------------------------------- #
def semantic_vs_categorical(predict, states_by_subject, test_subjects, k, corpus, seed=0):
    m = eval_predictor(predict, states_by_subject, test_subjects, k, corpus)
    return {
        "semantic_cosine": _mean_ci(m.semantic, seed),
        "category_accuracy": _mean_ci(m.categorical, seed),
    }


# --------------------------------------------------------------------------- #
# 4. Cross-subject generalization (per-test-subject distribution)
# --------------------------------------------------------------------------- #
def cross_subject(predict, states_by_subject, test_subjects, k, corpus, seed=0):
    m = eval_predictor(predict, states_by_subject, test_subjects, k, corpus)
    sem = np.asarray(m.semantic)
    return {
        "n_test_subjects": len(sem),
        "per_subject_semantic": m.semantic,
        "mean_ci": _mean_ci(m.semantic, seed),
        "frac_above_marginal": None,  # filled by caller with B0 level
    }


# --------------------------------------------------------------------------- #
# 5. History-depth curve
# --------------------------------------------------------------------------- #
def history_depth_curve(fit_fn, states_by_subject, test_subjects, corpus,
                        ks=(1, 2, 3, 4, 5, 8, 12), seed=0):
    """``fit_fn(k)`` returns a predictor fit for history window k (on train)."""
    curve = {}
    for k in ks:
        m = eval_predictor(fit_fn(k), states_by_subject, test_subjects, k, corpus)
        curve[k] = _mean_ci(m.semantic, seed)
    return curve


# --------------------------------------------------------------------------- #
# 6. Permutation null control
# --------------------------------------------------------------------------- #
def permutation_null(predict, states_by_subject, test_subjects, k, corpus,
                     n_null: int = 200, seed: int = 0) -> dict:
    """Observed metric vs a null where each history is paired with a RANDOM
    target (preserving marginals, destroying the temporal correspondence)."""
    rng = np.random.default_rng(seed)
    # collect all test samples + their actual targets
    all_samples, all_targets = [], []
    for sub in test_subjects:
        st = states_by_subject[sub]
        for s in build_prospective_samples(st, k=k):
            all_samples.append((sub, s))
            all_targets.append(st[s.target_index].embedding)
    targets = np.vstack(all_targets)

    def metric_with_targets(target_vecs) -> float:
        vals = []
        for (sub, s), tgt in zip(all_samples, target_vecs, strict=True):
            st = states_by_subject[sub]
            pred = predict(s, st, corpus)
            if pred.embedding is not None:
                vals.append(cosine(pred.embedding, tgt))
        return float(np.mean(vals)) if vals else float("nan")

    observed = metric_with_targets(all_targets)
    nulls = np.empty(n_null)
    for b in range(n_null):
        perm = rng.permutation(len(targets))
        nulls[b] = metric_with_targets(targets[perm])
    p = float((nulls >= observed).mean())
    return {
        "observed": observed,
        "null_mean": float(nulls.mean()),
        "null_ci": (float(np.percentile(nulls, 2.5)), float(np.percentile(nulls, 97.5))),
        "p_value": p,
        "n_null": n_null,
    }
