"""CM-LAB §32-35: Uncertainty, calibration, and selective prediction.

Scientific question (§32): can the model know when it is likely to be wrong?

Dataset: ds006067 thought-stream (the primary strong-signal dataset, the CM-2/CM-3
model's intended operating regime). Subject-disjoint split verified against the frozen
CM-2 seal. Model fit on TRAIN only; all uncertainty estimates use TRAIN statistics only
(no test-set tuning, no leakage).

Uncertainty sources (simple + interpretable first, §32):
  U1 distance_from_manifold : 1 - max cosine similarity of the history to TRAIN histories.
  U2 local_residual_var     : mean squared residual norm over the k nearest TRAIN histories.
  U3 bootstrap_disagreement : variance of B bootstrap-Ridge predictions for the history.
  U4 neighborhood_dispersion: mean pairwise cosine distance among the k nearest TRAIN targets.

Calibration (§33): Spearman/Pearson(uncertainty, error), uncertainty-decile mean error,
AUROC for large-error events, bootstrap predictive-interval coverage.
Selective prediction (§34): coverage-risk curves vs random abstention.
Decision (§35): CMUNC_CALIBRATED / CMUNC_WEAK / CMUNC_NOT_CALIBRATED.

Usage:
    .venv/bin/python data/scripts/cm_uncertainty.py
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np

from causal_mind.data import osf_a56rm
from causal_mind.eval import protocol
from causal_mind.forecast.multihorizon_model import LinearMultiHorizon
from causal_mind.thought import encode, state_v1
from causal_mind.thought.multihorizon import build_horizon_samples

ROOT = Path("/home/jovyan/work/causal-mind-v2")
OUT = ROOT / "reports" / "cm_uncertainty"
EMB_CACHE = Path("/home/jovyan/work/xval_scratch/ds006067_embeddings.npz")
SEED = 20260911          # frozen CM-2/CM-3 seed
K = 3
H = 1                     # primary horizon
ALPHA = 100.0
K_NN = 20                 # nearest TRAIN neighbors for U1/U2/U4
B_BOOT = 100              # bootstrap models for U3
N_DECILE = 10


def _data_key() -> str:
    h = hashlib.sha256()
    files = sorted(osf_a56rm.DERIVED.glob("*_thoughts.tsv"))
    for p in files:
        h.update(p.name.encode())
        h.update(str(p.stat().st_size).encode())
    return h.hexdigest()[:16]


def load_and_embed() -> tuple[dict[str, list], list[str]]:
    subs = osf_a56rm.all_subjects()
    key = _data_key()
    if EMB_CACHE.exists():
        try:
            cache = np.load(EMB_CACHE, allow_pickle=False)
            if str(cache["data_key"]) == key:
                csub = cache["subjects"].tolist()
                cidx = cache["indices"].tolist()
                vecs = cache["vectors"]
                states_by_sub: dict[str, list] = {}
                for s in subs:
                    states_by_sub[s] = state_v1.states_from_events(s, osf_a56rm.load_thought_events(s))
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
            all_idx.append((s, i))
            all_vecs.append(t.embedding)
    np.savez(EMB_CACHE,
             data_key=np.array(key),
             subjects=np.array([s for s, _ in all_idx]),
             indices=np.array([i for _, i in all_idx]),
             vectors=np.asarray(all_vecs, dtype=np.float32))
    return states_by_sub, subs


def _hist_vec(st, sample) -> np.ndarray:
    return np.concatenate([st[i].embedding for i in sample.history])


def _target_vec(st, sample) -> np.ndarray:
    return st[sample.target_index].embedding


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    def rank(a):
        order = a.argsort()
        ranks = np.empty_like(order, dtype=float)
        ranks[order] = np.arange(len(a))
        return ranks
    rx, ry = rank(np.asarray(x)), rank(np.asarray(y))
    rx = (rx - rx.mean()) / (rx.std() + 1e-12)
    ry = (ry - ry.mean()) / (ry.std() + 1e-12)
    return float(np.mean(rx * ry))


def auroc(scores: np.ndarray, labels: np.ndarray) -> float:
    scores = np.asarray(scores)
    labels = np.asarray(labels)
    if len(np.unique(labels)) < 2:
        return float("nan")
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    # rank-based (Mann-Whitney U)
    allv = np.concatenate([pos, neg])
    ranks = allv.argsort().argsort().astype(float) + 1
    r_pos = ranks[:len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    states_by_sub, subs = load_and_embed()
    split = protocol.subject_disjoint_split(subs, seed=SEED)
    assert protocol.verify_seal(split, SEED, len(subs)), "CM-2 SEAL MISMATCH"
    train, val, test = list(split.train), list(split.val), list(split.test)
    km = state_v1.fit_categories([st for s in train for st in states_by_sub[s]],
                                 n_clusters=16, seed=SEED)
    for s in subs:
        state_v1.assign_categories(states_by_sub[s], km)
    print(f"[unc] {len(subs)} subjects; split {len(train)}/{len(val)}/{len(test)}; seal OK")

    # Build train + test sample arrays (horizon H).
    tr_samples = [s for s in train for s in build_horizon_samples(states_by_sub[s], K, H)]
    te_samples = [(sub, s) for sub in test for s in build_horizon_samples(states_by_sub[sub], K, H)]
    X_train = np.stack([_hist_vec(states_by_sub[s.subject], s) for s in tr_samples])
    Y_train = np.stack([_target_vec(states_by_sub[s.subject], s) for s in tr_samples])
    X_test = np.stack([_hist_vec(states_by_sub[sub], s) for sub, s in te_samples])
    Y_test = np.stack([_target_vec(states_by_sub[sub], s) for sub, s in te_samples])
    print(f"[unc] train samples={len(X_train)} test samples={len(X_test)} "
          f"(hist dim={X_train.shape[1]})")

    # Fit the frozen linear model on TRAIN.
    model = LinearMultiHorizon(k=K, alpha=ALPHA, horizons=(H,))
    model.fit({H: tr_samples}, states_by_sub)
    pred_test = np.stack([model.predict(s, states_by_sub[sub]) for sub, s in te_samples])
    pred_train = np.stack([model.predict(s, states_by_sub[s.subject]) for s in tr_samples])

    # Actual error: 1 - cosine(pred, actual).
    err = np.array([1.0 - protocol.cosine(p, y) for p, y in zip(pred_test, Y_test)])

    # --- U1: distance from training manifold (1 - max cosine to TRAIN histories) ---
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=K_NN, metric="cosine").fit(X_train)
    dist, idx = nn.kneighbors(X_test)
    u1 = dist[:, 0]  # cosine distance to nearest TRAIN history (0=on manifold, 2=orthogonal)

    # --- U2: local residual variance (over k nearest TRAIN histories) ---
    resid_train = Y_train - pred_train  # (N_train, 384)
    resid_sq = np.einsum("ij,ij->i", resid_train, resid_train)
    u2 = resid_sq[idx].mean(axis=1)

    # --- U4: predictive-neighborhood dispersion (k nearest TRAIN targets) ---
    Y_nn = Y_train[idx]  # (N_test, K_NN, 384)
    # mean pairwise cosine distance within each neighborhood
    Y_nn_n = Y_nn / (np.linalg.norm(Y_nn, axis=2, keepdims=True) + 1e-12)
    gram = np.einsum("nkd,nld->nkl", Y_nn_n, Y_nn_n)  # (N_test, K_NN, K_NN)
    off = 1.0 - gram
    mask = ~np.eye(K_NN, dtype=bool)
    u4 = (off * mask).sum(axis=(1, 2)) / (K_NN * (K_NN - 1))

    # --- U3: bootstrap model disagreement (variance of B bootstrap predictions) ---
    rng = np.random.default_rng(SEED)
    n_tr = len(X_train)
    boot_preds = np.empty((B_BOOT, len(X_test), Y_train.shape[1]))
    from sklearn.linear_model import Ridge
    for b in range(B_BOOT):
        samp = rng.integers(0, n_tr, size=n_tr)
        rb = Ridge(alpha=ALPHA).fit(X_train[samp], Y_train[samp])
        boot_preds[b] = rb.predict(X_test)
    boot_mean = boot_preds.mean(axis=0)          # (N_test, 384)
    dev = boot_preds - boot_mean                  # (B, N_test, 384)
    u3 = (dev ** 2).mean(axis=0).mean(axis=1)     # (N_test,) mean sq deviation over models+dims

    unc = {
        "U1_distance_from_manifold": u1,
        "U2_local_residual_var": u2,
        "U3_bootstrap_disagreement": u3,
        "U4_neighborhood_dispersion": u4,
    }

    # --- §33 Calibration ---
    calib = {}
    for name, u in unc.items():
        u = np.asarray(u)
        sp = spearman(u, err)
        pe = float(np.corrcoef(u, err)[0, 1])
        # decile mean error (bin by uncertainty)
        q = np.quantile(u, np.linspace(0, 1, N_DECILE + 1))
        bins = np.clip(np.searchsorted(q, u, side="right") - 1, 0, N_DECILE - 1)
        dec_err = [float(err[bins == i].mean()) if np.any(bins == i) else float("nan")
                   for i in range(N_DECILE)]
        # AUROC for large-error events (top quartile = positive)
        thr = np.quantile(err, 0.75)
        labels = (err >= thr).astype(int)
        auc = auroc(u, labels)
        calib[name] = {
            "spearman": round(sp, 4), "pearson": round(pe, 4),
            "decile_mean_error": [round(x, 4) for x in dec_err],
            "auroc_large_error": round(auc, 4),
            "mono": bool(dec_err[-1] > dec_err[0]),
        }
        print(f"  {name}: spearman={sp:.3f} pearson={pe:.3f} "
              f"auroc={auc:.3f} dec_err[{dec_err[0]:.3f}->{dec_err[-1]:.3f}]")

    # NOTE: traditional predictive-interval COVERAGE is not well-defined here because the
    # target is a single embedding (a point), not a scalar. The bootstrap gives a cloud of
    # predicted points; "coverage" of a point target by that cloud has no standard meaning.
    # We therefore assess calibration via rank correlation, AUROC, and decile monotonicity
    # (above), and report the bootstrap prediction spread (U3) as the interval WIDTH.
    # (A naive coverage that compares the main model's cosine to the bootstrap cosines'
    # percentile interval is circular -- the main model is ~the bootstrap mean -- and is
    # deliberately NOT reported.)
    cos_boot = np.array([
        [protocol.cosine(boot_preds[b, i], Y_test[i]) for b in range(B_BOOT)]
        for i in range(len(X_test))
    ])  # (N_test, B)
    interval_width90 = float(np.mean(np.percentile(cos_boot, 95, axis=1)
                                     - np.percentile(cos_boot, 5, axis=1)))

    # --- §34 Selective prediction: coverage-risk curves ---
    # confidence = 1 - normalized uncertainty (higher = more confident).
    selective = {}
    for name, u in unc.items():
        u = np.asarray(u)
        conf = -(u - u.mean()) / (u.std() + 1e-12)  # higher conf = lower uncertainty
        fracs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        curve = []
        for f in fracs:
            thr = np.quantile(conf, 1.0 - f)  # keep top-f confidence
            keep = conf >= thr
            if np.sum(keep) == 0:
                continue
            curve.append({"coverage": round(float(np.mean(keep)), 3),
                          "mean_error": round(float(err[keep].mean()), 4)})
        # random abstention baseline (same coverage, random subset)
        rng2 = np.random.default_rng(SEED)
        rand_curve = []
        for f in fracs:
            keep = rng2.random(len(err)) < f
            if np.sum(keep) == 0:
                continue
            rand_curve.append({"coverage": round(float(np.mean(keep)), 3),
                               "mean_error": round(float(err[keep].mean()), 4)})
        selective[name] = {"curve": curve, "random_abstention": rand_curve}

    # --- §35 Decision ---
    # Use the best-calibrated uncertainty (by Spearman) as the representative.
    best = max(calib, key=lambda k: calib[k]["spearman"])
    best_sp = calib[best]["spearman"]
    best_auc = calib[best]["auroc_large_error"]
    n_mono = sum(1 for v in calib.values() if v["mono"] and v["spearman"] > 0)
    if best_sp >= 0.4 and best_auc >= 0.7:
        decision = "CMUNC_CALIBRATED"
    elif best_sp >= 0.1 and best_auc >= 0.55:
        decision = "CMUNC_WEAK"
    else:
        decision = "CMUNC_NOT_CALIBRATED"

    results = {
        "protocol": "CM-LAB S32-35 uncertainty/calibration/selective prediction",
        "dataset": "ds006067 thought-stream", "seed": SEED, "k": K, "h": H,
        "split": {"train": len(train), "val": len(val), "test": len(test)},
        "n_train_samples": int(len(X_train)), "n_test_samples": int(len(X_test)),
        "b_bootstrap": B_BOOT, "k_nn": K_NN,
        "mean_test_error": round(float(err.mean()), 4),
        "calibration": calib,
        "best_uncertainty": best,
        "n_mono_positive": int(n_mono),
        "bootstrap_interval_width_90pct": round(interval_width90, 4),
        "coverage_note": "predictive-interval coverage not well-defined for a single-embedding target; calibration assessed via rank corr / AUROC / decile monotonicity",
        "selective_prediction": selective,
        "decision": decision,
        "runtime_s": round(time.time() - t0, 1),
    }
    (OUT / "cm_uncertainty.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\n[unc] DECISION: {decision} (best={best}, spearman={best_sp:.3f}, auroc={best_auc:.3f}, "
          f"mono_positive={n_mono}/4)")
    print(f"[unc] bootstrap interval width (90pct)={interval_width90:.4f}")
    print(f"[unc] wrote {OUT / 'cm_uncertainty.json'} in {results['runtime_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
