"""CM-LAB §48-49: Forecast error taxonomy + error prediction.

  §48: an OUTCOME-blind, algorithmic taxonomy of LARGE forecast errors (top-quartile error).
      Categories (computed from the data, not hand-labeled):
        abrupt_jump      : actual target far from the history mean.
        gradual_drift    : actual target near the history mean but the prediction is far.
        high_local_entropy: the history's local neighborhood is diverse.
        rare_state       : actual target far from the TRAINING manifold.
        weak_history     : the k history entries are very similar (low variability).
        rep_ambiguity    : the prediction is similar to many same-subject targets (low specificity).
      Frequency among large-error events vs all events (enrichment).

  §49: use ONLY PRE-FORECAST information to predict whether the next forecast will be poor.
      Compare the §32-35 uncertainty sources vs simple heuristics (semantic volatility,
      distance-from-manifold, local entropy) by AUROC. If a simple heuristic wins, preserve it.

All fitting on TRAIN only. No test-set tuning. No CM-8 change.

Usage:
    .venv/bin/python data/scripts/cm_error_taxonomy.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from sklearn.neighbors import NearestNeighbors

from causal_mind.data import osf_a56rm
from causal_mind.eval import protocol
from causal_mind.forecast.multihorizon_model import LinearMultiHorizon
from causal_mind.thought import state_v1
from causal_mind.thought.multihorizon import build_horizon_samples

ROOT = Path("/home/jovyan/work/causal-mind-v2")
OUT = ROOT / "reports" / "cm_error_taxonomy"
EMB_CACHE = Path("/home/jovyan/work/xval_scratch/ds006067_embeddings.npz")
SEED = 20260911
K = 3
H = 1
ALPHA = 100.0
K_NN = 10


def load_states() -> tuple[dict[str, list], list[str]]:
    subs = osf_a56rm.all_subjects()
    import hashlib
    h = hashlib.sha256()
    for p in sorted(osf_a56rm.DERIVED.glob("*_thoughts.tsv")):
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
    raise RuntimeError("embedding cache missing")


def _l2n(X):
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def auroc(scores, labels):
    scores = np.asarray(scores); labels = np.asarray(labels)
    if len(np.unique(labels)) < 2:
        return float("nan")
    pos = scores[labels == 1]; neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    ranks = allv.argsort().argsort().astype(float) + 1
    r_pos = ranks[:len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    states_by_sub, subs = load_states()
    split = protocol.subject_disjoint_split(subs, seed=SEED)
    assert protocol.verify_seal(split, SEED, len(subs)), "CM-2 SEAL MISMATCH"
    train, val, test = list(split.train), list(split.val), list(split.test)
    print(f"[err] {len(subs)} subjects; split {len(train)}/{len(val)}/{len(test)}; seal OK")

    # Fit the frozen linear model on TRAIN.
    tr_samples = [s for s in train for s in build_horizon_samples(states_by_sub[s], K, H)]
    model = LinearMultiHorizon(k=K, alpha=ALPHA, horizons=(H,))
    model.fit({H: tr_samples}, states_by_sub)

    # TRAIN manifolds (history mean + target) for distance-from-manifold.
    tr_hist = np.stack([np.mean([states_by_sub[s.subject][i].embedding for i in s.history], axis=0) for s in tr_samples])
    tr_tgt = np.stack([states_by_sub[s.subject][s.target_index].embedding for s in tr_samples])
    nn_hist = NearestNeighbors(n_neighbors=1, metric="cosine").fit(_l2n(tr_hist))
    nn_tgt = NearestNeighbors(n_neighbors=1, metric="cosine").fit(_l2n(tr_tgt))

    # Per test sample: error + pre-forecast features + outcome-based taxonomy indicators.
    rows = []
    for sub in test:
        st = states_by_sub[sub]
        n = len(st)
        E = _l2n(np.stack([st[i].embedding for i in range(n)]))
        targets = E  # all same-subject entries
        for s in build_horizon_samples(st, K, H):
            hist = [st[i].embedding for i in s.history]
            hist_mean = np.mean(hist, axis=0)
            pred = model.predict(s, st)
            actual = st[s.target_index].embedding
            err = 1.0 - protocol.cosine(pred, actual)
            # pre-forecast features
            # semantic volatility: mean pairwise cosine distance among history entries
            Hn = _l2n(np.stack(hist))
            vol = float(1.0 - (Hn @ Hn.T)[np.triu_indices(K, 1)].mean())
            # distance from training manifold (history mean)
            _dm, _ = nn_hist.kneighbors(_l2n(np.asarray(hist_mean).reshape(1, -1)))
            d_manifold = float(_dm[0, 0])
            # local entropy: NN dispersion of the anchor in the subject's trajectory
            anchor = np.asarray(st[s.anchor_index].embedding).reshape(1, -1)
            d_anchor, _ = NearestNeighbors(n_neighbors=K_NN, metric="cosine").fit(E).kneighbors(_l2n(anchor))
            local_ent = float(d_anchor[0, 1:].mean())
            # weak history: history entries very similar (low volatility)
            weak_hist = vol < 0.1
            # outcome-based taxonomy indicators (use the actual target)
            abrupt_jump = (1.0 - protocol.cosine(actual, hist_mean)) > 0.5
            near_hist = (1.0 - protocol.cosine(actual, hist_mean)) < 0.3
            gradual_drift = near_hist and (err > 0.6)
            _rt, _ = nn_tgt.kneighbors(_l2n(np.asarray(actual).reshape(1, -1)))
            rare_state = float(_rt[0, 0]) > 0.5
            # rep ambiguity: prediction similar to many same-subject targets
            sim = targets @ _l2n(np.stack([pred]))[0]
            rep_ambig = int(np.sum(sim > 0.8)) > 5
            rows.append({
                "err": err, "vol": vol, "d_manifold": d_manifold, "local_ent": local_ent,
                "weak_hist": weak_hist, "abrupt_jump": abrupt_jump, "gradual_drift": gradual_drift,
                "high_local_entropy": local_ent > 0.5, "rare_state": rare_state, "rep_ambiguity": rep_ambig,
            })

    errs = np.array([r["err"] for r in rows])
    thr = np.quantile(errs, 0.75)
    large = errs >= thr
    n_large = int(large.sum())
    print(f"[err] {len(rows)} test samples; {n_large} large-error (top quartile, err>={thr:.3f})")

    # ---------- §48 taxonomy: frequency among large-error vs all events ----------
    cats = ["abrupt_jump", "gradual_drift", "high_local_entropy", "rare_state", "weak_hist", "rep_ambiguity"]
    taxonomy = {}
    for c in cats:
        all_frac = float(np.mean([r[c] for r in rows]))
        large_frac = float(np.mean([r[c] for r in rows if r["err"] >= thr])) if n_large else float("nan")
        enrichment = (large_frac / all_frac) if all_frac > 0 else float("nan")
        taxonomy[c] = {"all_events": round(all_frac, 4), "large_error": round(large_frac, 4),
                        "enrichment": round(enrichment, 3)}
    results: dict = {
        "protocol": "CM-LAB S48-49 error taxonomy + error prediction",
        "dataset": "ds006067 thought-stream", "seed": SEED, "k": K, "h": H,
        "split": {"train": len(train), "val": len(val), "test": len(test)},
        "n_test_samples": len(rows), "n_large_error": n_large, "large_error_threshold": round(float(thr), 4),
        "s48_taxonomy": taxonomy,
    }

    # ---------- §49 error prediction: pre-forecast features vs large-error ----------
    labels = large.astype(int)
    predictors = {
        "U1_distance_from_manifold": [r["d_manifold"] for r in rows],
        "U4_local_entropy": [r["local_ent"] for r in rows],
        "heuristic_semantic_volatility": [r["vol"] for r in rows],
    }
    aucs = {}
    for name, scores in predictors.items():
        aucs[name] = round(auroc(scores, labels), 4)
    results["s49_error_prediction"] = {
        "auroc_large_error": aucs,
        "note": "AUROC for predicting top-quartile error from PRE-FORECAST info only; "
                "a simple heuristic that wins is preserved",
    }

    # Decision: which predictor is best?
    best = max(aucs, key=aucs.get)
    best_auc = aucs[best]
    if best_auc >= 0.7:
        decision = "CMERR_PREDICTABLE"
    elif best_auc >= 0.55:
        decision = "CMERR_WEAKLY_PREDICTABLE"
    else:
        decision = "CMERR_NOT_PREDICTABLE"
    results["decision"] = decision
    results["best_predictor"] = best
    results["runtime_s"] = round(time.time() - t0, 1)

    (OUT / "cm_error_taxonomy.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"[err] taxonomy: " + ", ".join(f"{c}={taxonomy[c]['enrichment']}" for c in cats))
    print(f"[err] AUROC: {aucs}")
    print(f"[err] DECISION: {decision} (best={best}, auroc={best_auc})")
    print(f"[err] wrote {OUT / 'cm_error_taxonomy.json'} in {results['runtime_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
