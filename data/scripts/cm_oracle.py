"""CM-LAB §63-64: Oracle selective prediction + recursive depth.

  §63: use the best pre-forecast confidence (distance-from-manifold, from §32-35/§48-49) to
      SELECTIVELY predict. Report the accuracy-vs-coverage curve.
  §64: RECURSIVE depth L0..L3: rollout where the model's own prediction replaces the oldest
      history entry at each step. Track how accuracy degrades as the history becomes
      increasingly self-predicted (error accumulation / performative effect).

All fitting on TRAIN only. No test-set tuning. No CM-8 change.

Usage:
    .venv/bin/python data/scripts/cm_oracle.py
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
OUT = ROOT / "reports" / "cm_oracle"
EMB_CACHE = Path("/home/jovyan/work/xval_scratch/ds006067_embeddings.npz")
SEED = 20260911
K = 3
H = 1
ALPHA = 100.0


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


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    states_by_sub, subs = load_states()
    split = protocol.subject_disjoint_split(subs, seed=SEED)
    assert protocol.verify_seal(split, SEED, len(subs)), "CM-2 SEAL MISMATCH"
    train, val, test = list(split.train), list(split.val), list(split.test)
    print(f"[ora] {len(subs)} subjects; split {len(train)}/{len(val)}/{len(test)}; seal OK")

    tr_samples = [s for s in train for s in build_horizon_samples(states_by_sub[s], K, H)]
    model = LinearMultiHorizon(k=K, alpha=ALPHA, horizons=(H,))
    model.fit({H: tr_samples}, states_by_sub)
    ridge = model._ridges[H]

    def predict_from_hist(hist: list[np.ndarray]) -> np.ndarray:
        x = np.concatenate([np.asarray(e).reshape(-1) for e in hist])
        return ridge.predict(x.reshape(1, -1))[0]

    # TRAIN manifold (history mean) for distance-from-manifold confidence.
    tr_hist = np.stack([np.mean([states_by_sub[s.subject][i].embedding for i in s.history], axis=0) for s in tr_samples])
    nn_hist = NearestNeighbors(n_neighbors=1, metric="cosine").fit(_l2n(tr_hist))

    # ---------- §63 Oracle selective prediction ----------
    rows = []
    for sub in test:
        st = states_by_sub[sub]
        for s in build_horizon_samples(st, K, H):
            hist = [st[i].embedding for i in s.history]
            hist_mean = np.mean(hist, axis=0)
            pred = model.predict(s, st)
            actual = st[s.target_index].embedding
            err = 1.0 - protocol.cosine(pred, actual)
            _dm, _ = nn_hist.kneighbors(_l2n(np.asarray(hist_mean).reshape(1, -1)))
            conf = 1.0 - float(_dm[0, 0])
            rows.append({"err": err, "conf": conf})

    errs = np.array([r["err"] for r in rows])
    confs = np.array([r["conf"] for r in rows])
    full_acc = float(1.0 - errs.mean())

    coverage_curve: dict = {}
    for c in [0.10, 0.25, 0.50, 0.75, 0.90]:
        n_sel = max(1, int(len(rows) * c))
        idx = np.argsort(-confs)[:n_sel]
        sel_acc = float(1.0 - errs[idx].mean())
        coverage_curve[f"cov_{int(c * 100)}"] = {"coverage": c, "selected": int(n_sel), "accuracy": round(sel_acc, 4)}

    # ---------- §64 Recursive depth L0..L3 ----------
    depth_errors: dict[int, list] = {d: [] for d in range(K + 1)}
    for sub in test:
        st = states_by_sub[sub]
        n = len(st)
        if n < K + 2:
            continue
        hist = [np.array(st[i].embedding) for i in range(K)]
        n_pred = 0
        for t in range(K, n):
            pred = predict_from_hist(hist)
            actual = st[t].embedding
            err = 1.0 - protocol.cosine(pred, actual)
            depth_errors[n_pred].append(err)
            hist = hist[1:] + [np.array(pred)]
            n_pred = min(n_pred + 1, K)

    depth_acc: dict = {}
    for d in range(K + 1):
        if depth_errors[d]:
            depth_acc[f"L{d}"] = {"depth": d, "n": len(depth_errors[d]),
                                   "accuracy": round(float(1.0 - np.mean(depth_errors[d])), 4)}

    results: dict = {
        "protocol": "CM-LAB S63-64 Oracle selective prediction + recursive depth",
        "dataset": "ds006067 thought-stream", "seed": SEED, "k": K, "h": H,
        "split": {"train": len(train), "val": len(val), "test": len(test)},
        "s63_selective": {
            "full_coverage_accuracy": round(full_acc, 4),
            "accuracy_vs_coverage": coverage_curve,
            "confidence": "distance-from-manifold (1 - nn cosine distance to TRAIN history manifold)",
        },
        "s64_recursive": {
            "accuracy_by_depth": depth_acc,
            "note": "L0 = all-real history; Ld = the d most-recent history entries are the model's own predictions",
        },
    }

    # Decision
    best_sel = max(coverage_curve.values(), key=lambda x: x["accuracy"])
    sel_gain = best_sel["accuracy"] - full_acc
    l0 = depth_acc.get("L0", {}).get("accuracy", 0.0)
    lK = depth_acc.get(f"L{K}", {}).get("accuracy", 0.0)
    depth_degradation = l0 - lK
    if sel_gain > 0.02 and depth_degradation < 0.05:
        decision = "CMORACLE_USEFUL"
    elif sel_gain > 0.02:
        decision = "CMORACLE_SELECTIVE_ONLY"
    else:
        decision = "CMORACLE_LIMITED"
    results["decision"] = decision
    results["sel_gain_best"] = round(float(sel_gain), 4)
    results["depth_degradation_L0_to_L3"] = round(float(depth_degradation), 4)
    results["runtime_s"] = round(time.time() - t0, 1)

    (OUT / "cm_oracle.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"[ora] full_acc={full_acc:.4f}; coverage: " + ", ".join(f"{k}={v['accuracy']}" for k, v in coverage_curve.items()))
    print(f"[ora] depth: " + ", ".join(f"{k}={v['accuracy']}" for k, v in depth_acc.items()))
    print(f"[ora] sel_gain={sel_gain:.4f}; depth_degradation={depth_degradation:.4f}")
    print(f"[ora] DECISION: {decision}")
    print(f"[ora] wrote {OUT / 'cm_oracle.json'} in {results['runtime_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
