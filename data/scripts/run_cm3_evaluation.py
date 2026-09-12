"""CM-3 decisive evaluation: Future Predictability Curve + Thought Predictive Horizon.

Frozen protocol (seal in data/manifests/cm3_protocol_seal.json). Preserves the CM-2
split. For each event horizon h: fit the linear multi-horizon model on TRAIN,
select the strongest frozen baseline on VAL, evaluate model + baselines on the
sealed TEST, and compute PredictiveGain(h) = Model(h) - StrongBaseline(h) with
subject-level CIs. Also: history-depth x horizon matrix, time horizons, topic/
category targets, and the two frozen nulls.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from causal_mind.data import osf_a56rm
from causal_mind.eval import protocol
from causal_mind.eval.protocol import bootstrap_ci
from causal_mind.forecast import baselines_h
from causal_mind.forecast.multihorizon_model import LinearMultiHorizon
from causal_mind.thought import encode, state_v1
from causal_mind.thought.multihorizon import build_horizon_samples, build_time_horizon_samples

OUT = Path("/home/jovyan/work/causal-mind-v2/reports")
SEED = 20260911
HORIZONS = (1, 2, 3, 4, 5, 6, 8, 10)
TIME_HORIZONS = (30, 60, 120, 180)
K_DEFAULT = 3


def _eval_semantic(predict, states_by_sub, subjects, k, h, corpus, c1):
    """Per-subject mean cosine of predicted vs actual T[t+h] embedding."""
    per_sub = []
    for sub in subjects:
        st = states_by_sub[sub]
        coses = []
        for s in build_horizon_samples(st, k, h):
            pred = predict(s, st, corpus, c1)
            coses.append(protocol.cosine(pred, st[s.target_index].embedding))
        if coses:
            per_sub.append(float(np.mean(coses)))
    return per_sub


def _ci(per_sub):
    return list(bootstrap_ci(np.asarray(per_sub), n_boot=2000, seed=SEED))


def main() -> int:
    t0 = time.time()
    subs = osf_a56rm.all_subjects()
    enc = encode.MiniLMEncoder()
    states_by_sub: dict[str, list] = {}
    for s in subs:
        st = state_v1.states_from_events(s, osf_a56rm.load_thought_events(s))
        state_v1.embed_states(st, enc)
        states_by_sub[s] = st
    split = protocol.subject_disjoint_split(subs, seed=SEED)
    assert protocol.verify_seal(split, SEED, len(subs)), "CM-2 SEAL MISMATCH"
    train, val, test = list(split.train), list(split.val), list(split.test)
    train_states = [st for s in train for st in states_by_sub[s]]
    km = state_v1.fit_categories(train_states, n_clusters=16, seed=SEED)
    for s in subs:
        state_v1.assign_categories(states_by_sub[s], km)
    print(f"[cm3] {len(subs)} subjects; split {len(train)}/{len(val)}/{len(test)}; "
          f"seal verified")

    results: dict = {"n_subjects": len(subs), "split": {"train": len(train),
                     "val": len(val), "test": len(test)},
                     "seal": json.loads(protocol.SEAL_PATH.read_text())["seal"],
                     "k_default": K_DEFAULT, "horizons": list(HORIZONS)}

    # --- per-horizon: model + baselines, strong baseline selected on VAL ---
    fpc = {}
    for h in HORIZONS:
        corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, h, K_DEFAULT)
        c1 = baselines_h.HorizonCorpus.build(states_by_sub, train, 1, K_DEFAULT)
        bl = baselines_h.baselines_for(corpus, c1)
        # model fit on train for this horizon
        tr_samples = {}
        for hh in (h,):
            tr_samples[hh] = []
            for s in train:
                tr_samples[hh].extend(build_horizon_samples(states_by_sub[s], K_DEFAULT, hh))
        model = LinearMultiHorizon(k=K_DEFAULT, alpha=100.0, horizons=(h,))
        model.fit(tr_samples, states_by_sub)
        model_pred = lambda s, st, cc, cc1, _m=model: _m.predict(s, st)  # noqa: E731
        # select strongest baseline on VAL
        val_scores = {}
        for name, fn in bl.items():
            val_scores[name] = float(np.mean(_eval_semantic(
                lambda s, st, cc, cc1, fn=fn: fn(s, st, cc),
                states_by_sub, val, K_DEFAULT, h, corpus, c1)))
        strong = max(val_scores, key=val_scores.get)
        # test
        m_test = _eval_semantic(model_pred, states_by_sub, test, K_DEFAULT, h, corpus, c1)
        _strong_fn = bl[strong]
        b_test = _eval_semantic(lambda s, st, cc, cc1, _f=_strong_fn: _f(s, st, cc),
                                states_by_sub, test, K_DEFAULT, h, corpus, c1)
        m_ci, b_ci = _ci(m_test), _ci(b_test)
        gain = _ci(np.asarray(m_test) - np.asarray(b_test))
        fpc[h] = {
            "model": m_ci, "strong_baseline": strong, "strong_baseline_ci": b_ci,
            "gain": gain, "val_baseline_scores": {k: round(v, 4) for k, v in val_scores.items()},
        }
        print(f"  h={h:2d}: model={m_ci[0]:.4f} vs {strong}={b_ci[0]:.4f} "
              f"gain={gain[0]:+.4f} [{gain[1]:+.4f},{gain[2]:+.4f}]")
    results["FPC_semantic"] = fpc

    # --- Thought Predictive Horizon (semantic) ---
    results["TPH_semantic"] = _compute_tph(fpc, test, states_by_sub)

    # --- history-depth x horizon matrix (semantic gain vs B0 marginal) ---
    results["history_horizon_matrix"] = _hh_matrix(states_by_sub, train, val, test)

    # --- time horizons (semantic, model vs B0) ---
    results["time_horizons"] = _time_horizons(states_by_sub, train, val, test)

    # --- topic/category targets (model via nearest-centroid vs B0) ---
    results["topic_category"] = _topic_category(states_by_sub, train, val, test)

    # --- nulls (time-shuffled + transition-destroyed) at the best horizon ---
    results["nulls"] = _nulls(states_by_sub, train, val, test)

    # --- entropy / branching (empirical spread of actual futures vs predicted) ---
    results["entropy_branching"] = _entropy(states_by_sub, train, test)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cm3_results.json").write_text(json.dumps(results, indent=2, default=float))
    print(f"[cm3] wrote {OUT/'cm3_results.json'} in {time.time()-t0:.0f}s")
    _write_report(results)
    return 0


def _compute_tph(fpc, test, states_by_sub):
    """Max h where gain>0, CI excludes 0, and >=60% of test subjects above baseline."""
    tph = 0
    for h in sorted(fpc):
        g = fpc[h]["gain"]
        if g[0] > 0 and g[1] > 0:  # CI excludes 0 (lower bound > 0)
            tph = h
    return {"tph": tph, "rule": "max h with gain>0 and 95% CI lower bound > 0"}


def _hh_matrix(states_by_sub, train, val, test):
    """semantic model score for k in {1,2,3,5} x h in {1,2,3,4,5} (test mean)."""
    ks, hs = (1, 2, 3, 5), (1, 2, 3, 4, 5)
    mat = {}
    for k in ks:
        for h in hs:
            corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, h, k)
            tr_samples = {h: []}
            for s in train:
                tr_samples[h].extend(build_horizon_samples(states_by_sub[s], k, h))
            model = LinearMultiHorizon(k=k, alpha=100.0, horizons=(h,))
            model.fit(tr_samples, states_by_sub)
            per_sub = _eval_semantic(lambda s, st, cc, cc1, _m=model: _m.predict(s, st),
                                     states_by_sub, test, k, h, corpus, corpus)
            mat[f"k={k},h={h}"] = round(float(np.mean(per_sub)), 4)
    return mat


def _time_horizons(states_by_sub, train, val, test):
    out = {}
    for dt in TIME_HORIZONS:
        corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, 1, K_DEFAULT)
        # model: fit on train time-horizon samples (h varies; use a single map on hist)
        tr_samples = []
        for s in train:
            tr_samples.extend(build_time_horizon_samples(states_by_sub[s], K_DEFAULT, dt))
        if not tr_samples:
            continue
        # fit a linear map on the time-horizon samples (target = t+h which varies)
        from causal_mind.forecast.multihorizon_model import build_xy_h
        X, Y = build_xy_h(tr_samples, states_by_sub)
        from sklearn.linear_model import Ridge
        ridge = Ridge(alpha=100.0).fit(X, Y)
        per_sub = []
        for sub in test:
            st = states_by_sub[sub]
            coses = []
            for s in build_time_horizon_samples(st, K_DEFAULT, dt):
                x = np.concatenate([st[i].embedding for i in s.history])
                pred = ridge.predict(x.reshape(1, -1))[0]
                coses.append(protocol.cosine(pred, st[s.target_index].embedding))
            if coses:
                per_sub.append(float(np.mean(coses)))
        b0 = corpus.marginal
        b0_per_sub = []
        for sub in test:
            st = states_by_sub[sub]
            coses = [protocol.cosine(b0, st[s.target_index].embedding)
                     for s in build_time_horizon_samples(st, K_DEFAULT, dt)]
            if coses:
                b0_per_sub.append(float(np.mean(coses)))
        out[f"dt={dt}s"] = {"model": _ci(per_sub), "B0_marginal": _ci(b0_per_sub)}
    return out


def _topic_category(states_by_sub, train, val, test):
    """Topic/category predictability at each horizon via nearest train target."""
    out = {}
    for h in (1, 2, 3, 4, 5):
        corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, h, K_DEFAULT)
        cat_acc, topic_acc = [], []
        for sub in test:
            st = states_by_sub[sub]
            ca, ta = [], []
            for s in build_horizon_samples(st, K_DEFAULT, h):
                pred_emb = st[s.anchor_index].embedding  # persistence proxy
                sims = protocol.cosines(pred_emb, corpus.target)
                j = int(np.argmax(sims))
                ca.append(1.0 if corpus.target_cat[j] == st[s.target_index].category else 0.0)
                _tt = corpus.target_topic[j]
                _at = st[s.target_index].topic or ""
                ta.append(1.0 if _tt == _at else 0.0)
            if ca:
                cat_acc.append(float(np.mean(ca)))
                topic_acc.append(float(np.mean(ta)))
        out[f"h={h}"] = {"category_acc": _ci(cat_acc), "topic_acc": _ci(topic_acc)}
    return out


def _nulls(states_by_sub, train, val, test):
    """Time-shuffled + transition-destroyed nulls at h=3 (representative)."""
    h = 3
    corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, h, K_DEFAULT)
    tr_samples = {h: []}
    for s in train:
        tr_samples[h].extend(build_horizon_samples(states_by_sub[s], K_DEFAULT, h))
    model = LinearMultiHorizon(k=K_DEFAULT, alpha=100.0, horizons=(h,))
    model.fit(tr_samples, states_by_sub)
    observed = float(np.mean(_eval_semantic(
        lambda s, st, cc, cc1: model.predict(s, st),
        states_by_sub, test, K_DEFAULT, h, corpus, corpus)))
    rng = np.random.default_rng(SEED)
    # time-shuffled: shuffle each test subject's target order
    ts_nulls = []
    for _ in range(100):
        vals = []
        for sub in test:
            st = states_by_sub[sub]
            samps = build_horizon_samples(st, K_DEFAULT, h)
            order = rng.permutation(len(samps))
            for s in samps:
                tgt = samps[order[len(vals) % len(samps)]]
                pred = model.predict(s, st)
                vals.append(protocol.cosine(pred, st[tgt.target_index].embedding))
        ts_nulls.append(float(np.mean(vals)))
    # transition-destroyed: random same-subject history
    td_nulls = []
    for _ in range(100):
        vals = []
        for sub in test:
            st = states_by_sub[sub]
            samps = build_horizon_samples(st, K_DEFAULT, h)
            for s in samps:
                rand_hist = rng.integers(0, len(st) - 1, size=K_DEFAULT).tolist()
                x = np.concatenate([st[i].embedding for i in rand_hist])
                pred = model._ridges[h].predict(x.reshape(1, -1))[0]
                vals.append(protocol.cosine(pred, st[s.target_index].embedding))
        td_nulls.append(float(np.mean(vals)))
    return {
        "h": h, "observed": round(observed, 4),
        "time_shuffled": {"null_mean": round(float(np.mean(ts_nulls)), 4),
                          "p": round(float(np.mean(np.asarray(ts_nulls) >= observed)), 4)},
        "transition_destroyed": {"null_mean": round(float(np.mean(td_nulls)), 4),
                                 "p": round(float(np.mean(np.asarray(td_nulls) >= observed)), 4)},
    }


def _entropy(states_by_sub, train, test):
    """Empirical future spread: mean pairwise cosine among actual T[t+h] for a
    fixed anchor neighborhood, per horizon (lower = more diffuse future)."""
    out = {}
    for h in (1, 2, 3, 5):
        spreads = []
        for sub in test:
            st = states_by_sub[sub]
            n = len(st)
            if n < h + 5:
                continue
            # for anchors in the first half, the set of possible futures at h
            anchors = range(0, max(1, n // 2))
            fut = [st[t + h].embedding for t in anchors if t + h < n]
            if len(fut) < 5:
                continue
            sims = []
            for i in range(len(fut)):
                for j in range(i + 1, len(fut)):
                    sims.append(protocol.cosine(fut[i], fut[j]))
            spreads.append(float(np.mean(sims)))
        out[f"h={h}"] = {"mean_future_cosine": round(float(np.mean(spreads)), 4)} \
            if spreads else {"mean_future_cosine": None}
    return out


def _write_report(r: dict) -> None:
    def ci(x):
        return f"{x[0]:.4f} [{x[1]:.4f}, {x[2]:.4f}]"
    L = ["# CM-3 — MULTI-STEP COGNITIVE FUTURES (auto-generated)", ""]
    L.append(f"subjects={r['n_subjects']} split={r['split']} seal={r['seal'][:16]}... "
             f"k={r['k_default']}")
    L.append("\n## Future Predictability Curve (semantic; gain = model - strongest baseline)")
    for h in sorted(r["FPC_semantic"]):
        d = r["FPC_semantic"][h]
        L.append(f"- h={h:2d}: model {ci(d['model'])} vs {d['strong_baseline']} "
                 f"{ci(d['strong_baseline_ci'])} -> gain {d['gain'][0]:+.4f} "
                 f"[{d['gain'][1]:+.4f},{d['gain'][2]:+.4f}]")
    L.append(f"\n## Thought Predictive Horizon (semantic): {r['TPH_semantic']}")
    L.append("\n## History-depth x horizon (model semantic, test)")
    for k in (1, 2, 3, 5):
        row = [f"h={h}:{r['history_horizon_matrix'].get(f'k={k},h={h}', '-')}"
               for h in (1, 2, 3, 4, 5)]
        L.append(f"- k={k}: " + "  ".join(row))
    L.append("\n## Time horizons (semantic)")
    for k, v in r["time_horizons"].items():
        L.append(f"- {k}: model {ci(v['model'])} vs B0 {ci(v['B0_marginal'])}")
    L.append("\n## Topic / category (persistence-nearest)")
    for k, v in r["topic_category"].items():
        L.append(f"- {k}: category {ci(v['category_acc'])}  topic {ci(v['topic_acc'])}")
    L.append(f"\n## Nulls: {r['nulls']}")
    L.append(f"\n## Entropy / branching (mean future cosine): {r['entropy_branching']}")
    (OUT / "cm3_results.md").write_text("\n".join(L) + "\n")
    print(f"[cm3] wrote {OUT/'cm3_results.md'}")


if __name__ == "__main__":
    raise SystemExit(main())
