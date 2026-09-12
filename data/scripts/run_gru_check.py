"""GRU capacity check (CM-2E, Step 7): does a small GRU add headroom over the
linear transition model? Fit GRUNext on TRAIN (selected window k=3), evaluate
on the sealed TEST, compare to the linear model's 0.3623.
"""
from __future__ import annotations

import time

from causal_mind.data import osf_a56rm
from causal_mind.eval import analyses, protocol
from causal_mind.forecast import baselines, models
from causal_mind.thought import encode, state_v1

SEED = 20260911
K = 3  # the window selected for the linear model


def main() -> None:
    t0 = time.time()
    subs = osf_a56rm.all_subjects()
    enc = encode.MiniLMEncoder()
    states_by_sub: dict[str, list] = {}
    for s in subs:
        st = state_v1.states_from_events(s, osf_a56rm.load_thought_events(s))
        state_v1.embed_states(st, enc)
        states_by_sub[s] = st

    split = protocol.subject_disjoint_split(subs, seed=SEED)
    assert protocol.verify_seal(split, SEED, len(subs)), "SEAL MISMATCH"
    train_states = [st for s in split.train for st in states_by_sub[s]]
    km = state_v1.fit_categories(train_states, n_clusters=16, seed=SEED)
    for s in subs:
        state_v1.assign_categories(states_by_sub[s], km)
    corpus = baselines.TrainCorpus.build(train_states, n_clusters=16)

    # fit GRU on train (per-subject samples)
    samples = []
    for s in split.train:
        samples.extend(_samples(states_by_sub[s], K))
    X, Y = models.build_xy(samples, states_by_sub)
    print(f"[gru] train X={X.shape} Y={Y.shape}; fitting GRU (k={K})...")
    gru = models.GRUNext(k=K, dim=384, hidden=64, layers=1, epochs=30, seed=SEED)
    gru.fit(X, Y)

    def predict(sample, states, corpus_):
        return baselines.Prediction(embedding=gru.predict(sample, states))

    sc = analyses.eval_predictor(predict, states_by_sub, list(split.test), K, corpus)
    sem = analyses._mean_ci(sc.semantic, SEED)
    print(f"[gru] TEST semantic: {sem[0]:.4f} [{sem[1]:.4f}, {sem[2]:.4f}] "
          f"(linear was 0.3623 [0.3523, 0.3720])")
    print(f"[gru] params={gru.param_count()} in {time.time()-t0:.0f}s")


def _samples(states, k):
    from causal_mind.thought import prospective
    return prospective.build_prospective_samples(states, k=k)


if __name__ == "__main__":
    main()
