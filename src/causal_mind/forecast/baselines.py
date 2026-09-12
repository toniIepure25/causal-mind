"""Strong non-neural baselines B0-B7 (CM-2D).

The main model must beat these. All baselines are leakage-safe: they only use
TRAIN subjects' (state, next-state) pairs and the sample's own PAST history.

Targets:
* semantic  -> predicted next embedding (compared by cosine / retrieval rank)
* categorical -> predicted next coarse category (accuracy)
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from causal_mind.eval.protocol import cosines
from causal_mind.thought.prospective import Sample
from causal_mind.thought.state_v1 import ThoughtState


@dataclass
class Prediction:
    embedding: np.ndarray | None = None
    category: int | None = None


@dataclass
class TrainCorpus:
    """Precomputed TRAIN-subject structure used by the baselines."""
    emb_all: np.ndarray                      # (N_train_thoughts, dim)
    cat_all: np.ndarray                      # (N_train_thoughts,)
    trans_emb_t: list[np.ndarray] = field(default_factory=list)   # emb_t
    trans_emb_t1: list[np.ndarray] = field(default_factory=list)  # emb_{t+1}
    trans_cat_t1: list[int] = field(default_factory=list)         # cat_{t+1}
    cat_trans: np.ndarray | None = None      # (C, C) counts
    ngram2: dict[tuple[int, int], np.ndarray] = field(default_factory=dict)
    centroid: np.ndarray | None = None       # B0 marginal
    most_common_cat: int = 0
    n_clusters: int = 1

    @classmethod
    def build(cls, train_states: list[ThoughtState], n_clusters: int) -> TrainCorpus:
        emb = np.vstack([s.embedding for s in train_states])
        cat = np.array([s.category for s in train_states])
        c = cls(emb_all=emb, cat_all=cat, n_clusters=n_clusters)
        c.centroid = emb.mean(axis=0)
        c.most_common_cat = int(np.bincount(cat).argmax())
        # consecutive transitions within each train subject
        by_sub: dict[str, list[ThoughtState]] = {}
        for s in train_states:
            by_sub.setdefault(s.subject, []).append(s)
        C = n_clusters
        c.cat_trans = np.zeros((C, C), dtype=float)
        for st in by_sub.values():
            for a, b in zip(st, st[1:], strict=False):
                if a.embedding is None or b.embedding is None:
                    continue
                c.trans_emb_t.append(a.embedding)
                c.trans_emb_t1.append(b.embedding)
                c.trans_cat_t1.append(b.category)
                c.cat_trans[a.category, b.category] += 1
        # n-gram-2 (category): (cat_{t-1}, cat_t) -> counts of cat_{t+1}
        for st in by_sub.values():
            for i in range(1, len(st) - 1):
                a, b, d = st[i - 1], st[i], st[i + 1]
                key = (a.category, b.category)
                c.ngram2.setdefault(key, np.zeros(C, dtype=float))
                c.ngram2[key][d.category] += 1
        if c.trans_emb_t:
            c.trans_emb_t = np.vstack(c.trans_emb_t)
            c.trans_emb_t1 = np.vstack(c.trans_emb_t1)
            c.trans_cat_t1 = np.asarray(c.trans_cat_t1)
        return c


def _last(sample: Sample, states: list[ThoughtState]) -> ThoughtState:
    return states[sample.history[-1]]


# --------------------------------------------------------------------------- #
# B0 -- marginal (global train prior)
# --------------------------------------------------------------------------- #
def b0_marginal(sample, states, corpus: TrainCorpus) -> Prediction:
    return Prediction(embedding=corpus.centroid, category=corpus.most_common_cat)


# --------------------------------------------------------------------------- #
# B1 -- participant-independent previous state (use T_t only)
# --------------------------------------------------------------------------- #
def b1_previous_state(sample, states, corpus: TrainCorpus) -> Prediction:
    t = _last(sample, states)
    return Prediction(embedding=t.embedding, category=t.category)


# --------------------------------------------------------------------------- #
# B2 -- Markov  P(T_{t+1} | T_t)
# --------------------------------------------------------------------------- #
def b2_markov(sample, states, corpus: TrainCorpus) -> Prediction:
    t = _last(sample, states)
    pred = Prediction(embedding=t.embedding, category=t.category)  # fallback
    if corpus.cat_trans is not None:
        row = corpus.cat_trans[t.category]
        if row.sum() > 0:
            pred.category = int(np.argmax(row))
    if corpus.trans_emb_t is not None:
        sims = cosines(t.embedding, corpus.trans_emb_t)
        top = np.argsort(-sims)[:20]
        pred.embedding = corpus.trans_emb_t1[top].mean(axis=0)
    return pred


# --------------------------------------------------------------------------- #
# B3 -- multi-history Markov / n-gram  P(T_{t-1}, T_t)
# --------------------------------------------------------------------------- #
def b3_ngram(sample, states, corpus: TrainCorpus) -> Prediction:
    pred = b2_markov(sample, states, corpus)
    if len(sample.history) >= 2:
        a, b = states[sample.history[-2]], states[sample.history[-1]]
        counts = corpus.ngram2.get((a.category, b.category))
        if counts is not None and counts.sum() > 0:
            pred.category = int(np.argmax(counts))
    return pred


# --------------------------------------------------------------------------- #
# B4 -- semantic persistence (next ~ current semantic state)
# --------------------------------------------------------------------------- #
def b4_semantic_persistence(sample, states, corpus: TrainCorpus, alpha: float = 0.1) -> Prediction:
    t = _last(sample, states)
    emb = (1 - alpha) * t.embedding + alpha * corpus.centroid
    return Prediction(embedding=emb / (np.linalg.norm(emb) + 1e-9), category=t.category)


# --------------------------------------------------------------------------- #
# B5 -- semantic nearest-neighbour transition (THE strong baseline)
# --------------------------------------------------------------------------- #
def b5_semantic_nn(sample, states, corpus: TrainCorpus, nn: int = 10) -> Prediction:
    t = _last(sample, states)
    pred = Prediction(embedding=t.embedding, category=t.category)
    if corpus.trans_emb_t is not None:
        sims = cosines(t.embedding, corpus.trans_emb_t)
        top = np.argsort(-sims)[:nn]
        pred.embedding = corpus.trans_emb_t1[top].mean(axis=0)
        cats = np.bincount(corpus.trans_cat_t1[top], minlength=corpus.n_clusters)
        pred.category = int(cats.argmax())
    return pred


# --------------------------------------------------------------------------- #
# B6 -- participant-history (the subject's OWN past only; leakage-safe)
# --------------------------------------------------------------------------- #
def b6_participant_history(sample, states, corpus: TrainCorpus) -> Prediction:
    past = [states[i] for i in sample.history]
    if not past:
        return b0_marginal(sample, states, corpus)
    emb = np.vstack([s.embedding for s in past])
    cat = np.array([s.category for s in past])
    return Prediction(embedding=emb.mean(axis=0), category=int(np.bincount(cat).argmax()))


# --------------------------------------------------------------------------- #
# B7 -- frozen history retrieval over TRAIN (history, next) pairs
# --------------------------------------------------------------------------- #
def b7_history_retrieval(sample, states, corpus: TrainCorpus, nn: int = 5) -> Prediction:
    # represent the current history by its last state; retrieve train histories
    # (last state) most similar, predict their next state.
    t = _last(sample, states)
    pred = Prediction(embedding=t.embedding, category=t.category)
    if corpus.trans_emb_t is not None:
        sims = cosines(t.embedding, corpus.trans_emb_t)
        top = np.argsort(-sims)[:nn]
        pred.embedding = corpus.trans_emb_t1[top].mean(axis=0)
    return pred


BASELINES = {
    "B0_marginal": b0_marginal,
    "B1_previous_state": b1_previous_state,
    "B2_markov": b2_markov,
    "B3_ngram": b3_ngram,
    "B4_semantic_persistence": b4_semantic_persistence,
    "B5_semantic_nn": b5_semantic_nn,
    "B6_participant_history": b6_participant_history,
    "B7_history_retrieval": b7_history_retrieval,
}
