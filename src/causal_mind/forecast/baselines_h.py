"""Multi-horizon baselines B0-B7 + CM-2 linear (central) (CM-3D).

All baselines are leakage-safe: they use only TRAIN-subject (history -> future)
structure and the sample's own PAST history. For horizon h, the target is
T[t+h]; the input is history [t-k+1 .. t] (all <= t).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from causal_mind.eval.protocol import cosines
from causal_mind.thought.multihorizon import HorizonSample
from causal_mind.thought.state_v1 import ThoughtState


@dataclass
class HorizonCorpus:
    """Precomputed TRAIN structure for one horizon h."""
    h: int
    k: int
    anchor: np.ndarray          # (N, dim)  T[t]
    hist: np.ndarray            # (N, k*dim) history window (oldest->newest)
    target: np.ndarray          # (N, dim)  T[t+h]
    target_topic: list[str] = field(default_factory=list)
    target_cat: list[int] = field(default_factory=list)
    marginal: np.ndarray | None = None   # B0: mean target
    hist_mean: np.ndarray | None = None  # (N, dim) mean of each history window

    @classmethod
    def build(cls, states_by_subject: dict[str, list[ThoughtState]],
              train_subjects: list[str], h: int, k: int) -> HorizonCorpus:
        anchors, hists, targets, topics, cats = [], [], [], [], []
        for sub in train_subjects:
            st = states_by_subject[sub]
            n = len(st)
            for t in range(k - 1, n - h):
                hist = [st[i].embedding for i in range(t - k + 1, t + 1)]
                if any(e is None for e in hist) or st[t + h].embedding is None:
                    continue
                anchors.append(st[t].embedding)
                hists.append(np.concatenate(hist))
                targets.append(st[t + h].embedding)
                topics.append(st[t + h].topic or "")
                cats.append(st[t + h].category)
        c = cls(h=h, k=k,
                anchor=np.vstack(anchors), hist=np.vstack(hists),
                target=np.vstack(targets), target_topic=topics, target_cat=cats)
        c.marginal = c.target.mean(axis=0)
        dim = c.hist.shape[1] // k
        c.hist_mean = c.hist.reshape(-1, k, dim).mean(axis=1)
        return c


def _top_mean(c: HorizonCorpus, query: np.ndarray, which: str, nn: int) -> np.ndarray:
    """Mean of the top-nn train targets most similar to ``query`` (by which)."""
    src = {"anchor": c.anchor, "hist": c.hist, "hist_mean": c.hist_mean}[which]
    sims = cosines(query, src)
    top = np.argsort(-sims)[:nn]
    return c.target[top].mean(axis=0)


def b0_marginal_future(s: HorizonSample, states, c: HorizonCorpus):
    return c.marginal.copy()


def b1_persistence(s: HorizonSample, states, c: HorizonCorpus):
    return states[s.anchor_index].embedding.copy()


def b2_markov_iterated(s: HorizonSample, states, c1: HorizonCorpus, nn: int = 20):
    """Iterate the 1-step transition h times (c1 is the h=1 corpus)."""
    x = states[s.anchor_index].embedding.copy()
    for _ in range(s.h):
        sims = cosines(x, c1.anchor)
        top = np.argsort(-sims)[:nn]
        x = c1.target[top].mean(axis=0)
    return x


def b3_khistory(s: HorizonSample, states, c: HorizonCorpus, nn: int = 20):
    hist = np.concatenate([states[i].embedding for i in s.history])
    return _top_mean(c, hist, "hist", nn)


def b4_drift(s: HorizonSample, states, c: HorizonCorpus, alpha: float = 0.5):
    emb = (1 - alpha) * states[s.anchor_index].embedding + alpha * c.marginal
    return emb / (np.linalg.norm(emb) + 1e-9)


def b5_nn_anchor(s: HorizonSample, states, c: HorizonCorpus, nn: int = 20):
    return _top_mean(c, states[s.anchor_index].embedding, "anchor", nn)


def b6_population_avg(s: HorizonSample, states, c: HorizonCorpus):
    return c.marginal.copy()


def b7_frozen_lang_history(s: HorizonSample, states, c: HorizonCorpus, nn: int = 20):
    # strong frozen retrieval on the full text history (approx via history emb mean)
    hist = np.mean([states[i].embedding for i in s.history], axis=0)
    return _top_mean(c, hist, "hist_mean", nn)


def baselines_for(c: HorizonCorpus, c1: HorizonCorpus) -> dict[str, object]:
    return {
        "B0_marginal_future": b0_marginal_future,
        "B1_persistence": b1_persistence,
        "B2_markov_iterated": lambda s, st, cc: b2_markov_iterated(s, st, c1),
        "B3_khistory": b3_khistory,
        "B4_drift": b4_drift,
        "B5_nn_anchor": b5_nn_anchor,
        "B6_population_avg": b6_population_avg,
        "B7_frozen_lang_history": b7_frozen_lang_history,
    }
