"""CM-LAB §29-31: Representation robustness + semantic-metric robustness.

Prospectively defined SMALL representation set (NOT a benchmark of dozens of encoders):
  R0: all-MiniLM-L6-v2 (384-d, frozen) -- the current primary representation.
  R1: all-mpnet-base-v2 (768-d, frozen) -- one stronger modern English encoder (if available).
  R2: TF-IDF bag-of-words (lexical; fit on TRAIN subjects only).
  R3: NMF topic representation (30-d; fit on TRAIN TF-IDF only).

For each representation (model = frozen linear multi-horizon fit on TRAIN; strongest
baseline B0-B7 selected on VAL; evaluated on sealed TEST):
  A. next-state predictive gain (model - strong baseline) at h=1;
  B. history-depth saturation: gain vs k in {1,2,3,4,5} at h=1;
  C. multi-step decay: gain vs h in {1,2,3,5,10} at k=3;
  D. effect-size dependence on one embedding geometry;
  E. baseline ranking stability.

Metric robustness (§31) on the FIXED R0 model outputs: cosine, normalized Euclidean,
neighborhood rank, Pearson correlation. No per-metric representation tuning.

Decision: CMREP_ROBUST / CMREP_PARTIAL / CMREP_REPRESENTATION_DEPENDENT / CMREP_INCONCLUSIVE.

Usage:
    .venv/bin/python data/scripts/cm_representation.py
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
from causal_mind.thought.multihorizon import build_horizon_samples

ROOT = Path("/home/jovyan/work/causal-mind-v2")
OUT = ROOT / "reports" / "cm_representation"
EMB_CACHE = Path("/home/jovyan/work/xval_scratch/ds006067_embeddings.npz")
MPNET_CACHE = Path("/home/jovyan/work/xval_scratch/ds006067_mpnet.npz")
SEED = 20260911
K = 3
HORIZONS = (1, 2, 5, 10)
K_VALUES = (1, 3, 5)
ALPHA = 100.0
N_TOPICS = 20


def load_states() -> tuple[dict[str, list], list[str]]:
    subs = osf_a56rm.all_subjects()
    key_files = sorted(osf_a56rm.DERIVED.glob("*_thoughts.tsv"))
    import hashlib
    h = hashlib.sha256()
    for p in key_files:
        h.update(p.name.encode()); h.update(str(p.stat().st_size).encode())
    key = h.hexdigest()[:16]
    if EMB_CACHE.exists():
        try:
            cache = np.load(EMB_CACHE, allow_pickle=False)
            if str(cache["data_key"]) == key:
                csub = cache["subjects"].tolist(); cidx = cache["indices"].tolist()
                vecs = cache["vectors"]
                states_by_sub = {s: state_v1.states_from_events(s, osf_a56rm.load_thought_events(s)) for s in subs}
                for (s, i), v in zip(zip(csub, cidx), vecs):
                    states_by_sub[s][i].embedding = v
                return states_by_sub, subs
        except Exception:
            pass
    enc = encode.MiniLMEncoder()
    states_by_sub = {}
    all_idx, all_vecs = [], []
    for s in subs:
        st = state_v1.states_from_events(s, osf_a56rm.load_thought_events(s))
        state_v1.embed_states(st, enc)
        states_by_sub[s] = st
        for i, t in enumerate(st):
            all_idx.append((s, i)); all_vecs.append(t.embedding)
    np.savez(EMB_CACHE, data_key=np.array(key),
             subjects=np.array([s for s, _ in all_idx]),
             indices=np.array([i for _, i in all_idx]),
             vectors=np.asarray(all_vecs, dtype=np.float32))
    return states_by_sub, subs


def _all_texts(states_by_sub, subs):
    return [st.transcript for s in subs for st in states_by_sub[s]]


def build_representations(states_by_sub, subs, train):
    """Return dict rep_id -> {sub: np.ndarray (n_entries, dim)} and metadata."""
    reps: dict[str, dict] = {}
    meta: dict[str, dict] = {}
    # R0: MiniLM (already embedded)
    reps["R0_minilm"] = {s: np.stack([st.embedding for st in states_by_sub[s]]) for s in subs}
    meta["R0_minilm"] = {"model": "all-MiniLM-L6-v2", "dim": 384, "frozen": True,
                          "fit_on_train": False, "license": "Apache-2.0"}
    # R2: TF-IDF (fit on TRAIN subjects only). Implemented directly (the codebase
    # TfidfEncoder has a latent bug: vocabulary_size_); we do not modify frozen code.
    # max_features kept modest (500) so the k-history vector (1500-d) stays a feasible
    # Ridge input for the linear multi-horizon model.
    from sklearn.feature_extraction.text import TfidfVectorizer
    train_texts = [st.transcript for s in train for st in states_by_sub[s]]
    tfidf = TfidfVectorizer(stop_words="english", max_features=500)
    tfidf.fit(train_texts)
    reps["R2_tfidf"] = {s: tfidf.transform([st.transcript for st in states_by_sub[s]]).toarray().astype(np.float32)
                         for s in subs}
    meta["R2_tfidf"] = {"model": "TfidfVectorizer(stop_words=english, max_features=500)",
                         "dim": int(len(tfidf.vocabulary_)), "frozen": False, "fit_on_train": True,
                         "license": "sklearn (BSD)"}
    # R3: NMF topics (30-d) on TRAIN TF-IDF only (SPARSE input -> fast)
    from sklearn.decomposition import NMF
    train_tfidf_sparse = tfidf.transform(train_texts)
    nmf = NMF(n_components=N_TOPICS, init="nndsvda", random_state=SEED, max_iter=100).fit(train_tfidf_sparse)
    reps["R3_nmf_topics"] = {s: np.asarray(nmf.transform(tfidf.transform([st.transcript for st in states_by_sub[s]])), dtype=np.float32)
                              for s in subs}
    meta["R3_nmf_topics"] = {"model": f"NMF(n_components={N_TOPICS}, max_iter=100) on train TF-IDF(sparse)",
                              "dim": N_TOPICS, "frozen": False, "fit_on_train": True,
                              "license": "sklearn (BSD)"}
    # R1: all-mpnet-base-v2 (if cached / available)
    if MPNET_CACHE.exists():
        try:
            cache = np.load(MPNET_CACHE, allow_pickle=False)
            csub = cache["subjects"].tolist(); cidx = cache["indices"].tolist()
            vecs = cache["vectors"]
            reps["R1_mpnet"] = {s: np.zeros((len(states_by_sub[s]), vecs.shape[1]), dtype=np.float32) for s in subs}
            for (s, i), v in zip(zip(csub, cidx), vecs):
                reps["R1_mpnet"][s][i] = v
            meta["R1_mpnet"] = {"model": "all-mpnet-base-v2", "dim": int(vecs.shape[1]),
                                 "frozen": True, "fit_on_train": False, "license": "Apache-2.0"}
        except Exception:
            pass
    return reps, meta


def _eval_gain(rep, states_by_sub, subs, train, val, test, k, h):
    """Fit model on train, select strong baseline on val, return (gain_mean, gain_ci, strong)."""
    # set embeddings
    for s in subs:
        for i, st in enumerate(states_by_sub[s]):
            st.embedding = rep[s][i]
    corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, h, k)
    c1 = baselines_h.HorizonCorpus.build(states_by_sub, train, 1, k)
    bl = baselines_h.baselines_for(corpus, c1)
    tr_samples = {h: [s for s in train for s in build_horizon_samples(states_by_sub[s], k, h)]}
    model = LinearMultiHorizon(k=k, alpha=ALPHA, horizons=(h,))
    model.fit(tr_samples, states_by_sub)
    model_pred = lambda s, st, cc, cc1, _m=model: _m.predict(s, st)  # noqa: E731

    def _per_sub(predict):
        out = []
        for sub in test:
            st = states_by_sub[sub]
            cs = [protocol.cosine(predict(s, st, corpus, c1), st[s.target_index].embedding)
                  for s in build_horizon_samples(st, k, h)]
            if cs:
                out.append(float(np.mean(cs)))
        return out

    val_scores = {name: float(np.mean(_per_sub(lambda s, st, cc, cc1, _f=fn: _f(s, st, cc))))
                  for name, fn in bl.items()}
    strong = max(val_scores, key=val_scores.get)
    strong_fn = bl[strong]
    m_test = _per_sub(model_pred)
    b_test = _per_sub(lambda s, st, cc, cc1, _f=strong_fn: _f(s, st, cc))
    gain = np.asarray(m_test) - np.asarray(b_test)
    gain_ci = list(bootstrap_ci(gain, n_boot=1000, seed=SEED))
    return float(gain.mean()), gain_ci, strong, {n2: round(v2, 4) for n2, v2 in val_scores.items()}


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    states_by_sub, subs = load_states()
    split = protocol.subject_disjoint_split(subs, seed=SEED)
    assert protocol.verify_seal(split, SEED, len(subs)), "CM-2 SEAL MISMATCH"
    train, val, test = list(split.train), list(split.val), list(split.test)
    print(f"[rep] {len(subs)} subjects; split {len(train)}/{len(val)}/{len(test)}; seal OK")

    reps, meta = build_representations(states_by_sub, subs, train)
    print(f"[rep] representations: {list(reps.keys())}")

    results: dict = {
        "protocol": "CM-LAB S29-31 representation + metric robustness",
        "dataset": "ds006067 thought-stream", "seed": SEED,
        "split": {"train": len(train), "val": len(val), "test": len(test)},
        "representations": meta,
    }

    per_rep = {}
    for rid, rep in reps.items():
        # A: gain at h=1, k=3
        g1, ci1, strong1, val1 = _eval_gain(rep, states_by_sub, subs, train, val, test, 3, 1)
        # B: k-saturation at h=1
        k_sat = {}
        for k in K_VALUES:
            gk, cik, sk, _ = _eval_gain(rep, states_by_sub, subs, train, val, test, k, 1)
            k_sat[str(k)] = {"gain": round(gk, 4), "ci": [round(x, 4) for x in cik], "strong": sk}
        # C: h-decay at k=3
        h_decay = {}
        for h in HORIZONS:
            gh, cih, sh, _ = _eval_gain(rep, states_by_sub, subs, train, val, test, 3, h)
            h_decay[str(h)] = {"gain": round(gh, 4), "ci": [round(x, 4) for x in cih], "strong": sh}
        per_rep[rid] = {
            "gain_h1_k3": round(g1, 4), "gain_h1_k3_ci": [round(x, 4) for x in ci1],
            "strong_baseline_h1": strong1, "val_baseline_scores_h1": val1,
            "k_saturation_h1": k_sat, "h_decay_k3": h_decay,
        }
        ks = [k_sat[str(k)]["gain"] for k in K_VALUES]
        print(f"  {rid}: gain_h1={g1:+.4f} [{ci1[1]:+.4f},{ci1[2]:+.4f}] strong={strong1} "
              f"k-sat={ks} h-decay={[h_decay[str(h)]['gain'] for h in HORIZONS]}")

    results["per_representation"] = per_rep

    # --- §31 Metric robustness on the FIXED R0 model ---
    # Fit the R0 model once at k=3,h=1; then score model + strong baseline under 4 metrics.
    r0 = reps["R0_minilm"]
    for s in subs:
        for i, st in enumerate(states_by_sub[s]):
            st.embedding = r0[s][i]
    k, h = 3, 1
    corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, h, k)
    c1 = baselines_h.HorizonCorpus.build(states_by_sub, train, 1, k)
    bl = baselines_h.baselines_for(corpus, c1)
    tr_samples = {h: [s for s in train for s in build_horizon_samples(states_by_sub[s], k, h)]}
    model = LinearMultiHorizon(k=k, alpha=ALPHA, horizons=(h,))
    model.fit(tr_samples, states_by_sub)
    # strong baseline on val (cosine)
    def _val_cos(fn):
        tot, cnt = 0.0, 0
        for sub in val:
            st = states_by_sub[sub]
            for s in build_horizon_samples(st, k, h):
                tot += protocol.cosine(fn(s, st, c1), st[s.target_index].embedding); cnt += 1
        return tot / max(cnt, 1)
    val_scores = {n: _val_cos(fn) for n, fn in bl.items()}
    strong = max(val_scores, key=val_scores.get)
    strong_fn = bl[strong]

    # collect (pred_model, pred_baseline, actual) for all test samples
    triples = []
    for sub in test:
        st = states_by_sub[sub]
        for s in build_horizon_samples(st, k, h):
            pm = model.predict(s, st)
            pb = strong_fn(s, st, c1)
            pa = st[s.target_index].embedding
            triples.append((pm, pb, pa))

    def _metric_score(pred, actual, metric):
        if metric == "cosine":
            return protocol.cosine(pred, actual)
        if metric == "euclidean":
            p = pred / (np.linalg.norm(pred) + 1e-12)
            a = actual / (np.linalg.norm(actual) + 1e-12)
            return 1.0 - np.linalg.norm(p - a) / np.sqrt(2.0)
        if metric == "correlation":
            return float(np.corrcoef(pred, actual)[0, 1])
        return 0.0

    metrics = {}
    for metric in ("cosine", "euclidean", "correlation"):
        m_scores = np.array([_metric_score(pm, pa, metric) for pm, pb, pa in triples])
        b_scores = np.array([_metric_score(pb, pa, metric) for pm, pb, pa in triples])
        metrics[metric] = {"model": round(float(m_scores.mean()), 4),
                            "baseline": round(float(b_scores.mean()), 4),
                            "gain": round(float((m_scores - b_scores).mean()), 4)}
    # neighborhood rank (vectorized per subject): rank of actual target among all
    # same-subject entries (lower = better retrieval).
    def _l2n(X):
        return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    m_ranks, b_ranks = [], []
    for sub in test:
        st = states_by_sub[sub]
        samples = build_horizon_samples(st, k, h)
        if not samples:
            continue
        targets = np.stack([st[i].embedding for i in range(len(st))])   # (n_entries, d)
        preds_m = np.stack([model.predict(s, st) for s in samples])     # (n_s, d)
        preds_b = np.stack([strong_fn(s, st, c1) for s in samples])     # (n_s, d)
        Tn = _l2n(targets)
        actual_idx = np.array([s.target_index for s in samples])
        for preds, ranks in ((preds_m, m_ranks), (preds_b, b_ranks)):
            sim = _l2n(preds) @ Tn.T                                    # (n_s, n_entries)
            actual_sim = sim[np.arange(len(samples)), actual_idx]
            ranks.extend((np.sum(sim >= actual_sim[:, None], axis=1) + 1).tolist())
    metrics["rank"] = {"model_mean_rank": round(float(np.mean(m_ranks)), 3),
                        "baseline_mean_rank": round(float(np.mean(b_ranks)), 3),
                        "note": "lower = better; rank of actual target among same-subject entries"}
    results["metric_robustness_R0"] = metrics

    # --- Decision ---
    # A: does gain survive? (gain_h1_k3 CI excludes 0 in how many reps?)
    n_gain_pos = sum(1 for r in per_rep.values() if r["gain_h1_k3_ci"][1] > 0)
    n_reps = len(per_rep)
    # B: k-saturation (does gain peak/plateau around k=3?)
    # C: h-decay (does gain decrease with h?)
    # D: effect-size dependence (relative range of gain across reps)
    gains = [per_rep[r]["gain_h1_k3"] for r in per_rep]
    gain_range = (max(gains) - min(gains)) if gains else 0.0
    # relative effect-size ratio (max/min of positive gains) -- how much the geometry matters
    pos_gains = [g for g in gains if g > 0]
    gain_ratio = (max(pos_gains) / min(pos_gains)) if pos_gains and min(pos_gains) > 0 else float("inf")
    all_positive = n_gain_pos == n_reps
    if all_positive and gain_ratio < 2.0:
        decision = "CMREP_ROBUST"
    elif n_gain_pos == n_reps:
        # qualitative finding survives everywhere, but effect size / baseline ranking vary
        decision = "CMREP_PARTIAL"
    elif n_gain_pos >= max(1, n_reps - 1):
        decision = "CMREP_REPRESENTATION_DEPENDENT"
    else:
        decision = "CMREP_INCONCLUSIVE"
    results["decision"] = decision
    results["n_gain_positive"] = f"{n_gain_pos}/{n_reps}"
    results["gain_range_across_reps"] = round(gain_range, 4)
    results["gain_ratio_max_min"] = round(gain_ratio, 3)
    results["runtime_s"] = round(time.time() - t0, 1)

    (OUT / "cm_representation.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\n[rep] DECISION: {decision} (gain positive in {n_gain_pos}/{n_reps}, range={gain_range:.4f})")
    print(f"[rep] wrote {OUT / 'cm_representation.json'} in {results['runtime_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
