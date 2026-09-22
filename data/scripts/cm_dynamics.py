"""CM-LAB §41, §43-47: Local dynamics of the measured semantic trajectory.

Descriptive + predictive analyses of the measured semantic trajectory in the frozen MiniLM
representation (NOT a claim that "thought is linear" -- the object is the measured trajectory
in the chosen representation).

  §41 trajectory entropy: semantic velocity, local semantic entropy (NN dispersion),
      topic-switch rate; does higher local entropy predict worse forecasting?
  §43 local linearity: residual autocorrelation, local curvature.
  §44 nonlinear residual test: can a small k-NN predict the linear model's residuals on
      held-out subjects (incremental nonlinear structure)?
  §45 effective dimension: PCA participation ratio, explained variance, MLE intrinsic dim.
  §46 dimension vs predictability: across-subject correlation.
  §47 attractor-like structure: recurrence, dwell times, state persistence (autocorrelation).

All fitting/tuning on TRAIN only. Decision: CMDYN_* (descriptive; no confirmatory claim).

Usage:
    .venv/bin/python data/scripts/cm_dynamics.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.neighbors import NearestNeighbors

from causal_mind.data import osf_a56rm
from causal_mind.eval import protocol
from causal_mind.forecast.multihorizon_model import LinearMultiHorizon
from causal_mind.thought import state_v1
from causal_mind.thought.multihorizon import build_horizon_samples

ROOT = Path("/home/jovyan/work/causal-mind-v2")
OUT = ROOT / "reports" / "cm_dynamics"
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


def _spearman(x, y):
    def rank(a):
        o = a.argsort(); r = np.empty_like(o, dtype=float); r[o] = np.arange(len(a)); return r
    rx, ry = rank(np.asarray(x)), rank(np.asarray(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def mle_intrinsic_dim(X, rng):
    """Levina-Bickel MLE of intrinsic dimension (log-neighborhood)."""
    n = len(X)
    if n < 20:
        return float("nan")
    nn = NearestNeighbors(n_neighbors=3, metric="euclidean").fit(X)
    dist, _ = nn.kneighbors(X)
    e1 = dist[:, 1]  # NN distance
    e2 = dist[:, 2]  # 2nd NN distance
    e1 = np.clip(e1, 1e-12, None)
    e2 = np.clip(e2, 1e-12, None)
    return float(n / np.sum(np.log(e2 / e1)))


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    states_by_sub, subs = load_states()
    split = protocol.subject_disjoint_split(subs, seed=SEED)
    assert protocol.verify_seal(split, SEED, len(subs)), "CM-2 SEAL MISMATCH"
    train, val, test = list(split.train), list(split.val), list(split.test)
    km = state_v1.fit_categories([st for s in train for st in states_by_sub[s]], n_clusters=16, seed=SEED)
    for s in subs:
        state_v1.assign_categories(states_by_sub[s], km)
    print(f"[dyn] {len(subs)} subjects; split {len(train)}/{len(val)}/{len(test)}; seal OK")

    # Fit the frozen linear model on TRAIN (h=1).
    tr_samples = [s for s in train for s in build_horizon_samples(states_by_sub[s], K, H)]
    model = LinearMultiHorizon(k=K, alpha=ALPHA, horizons=(H,))
    model.fit({H: tr_samples}, states_by_sub)

    results: dict = {
        "protocol": "CM-LAB S41,S43-47 local dynamics (descriptive)",
        "dataset": "ds006067 thought-stream", "seed": SEED, "k": K, "h": H,
        "split": {"train": len(train), "val": len(val), "test": len(test)},
    }

    # ---------- §41 trajectory entropy + correlation with forecast error ----------
    per_subj_entropy = {}
    subj_err, subj_entropy = [], []
    for sub in subs:
        st = states_by_sub[sub]
        n = len(st)
        if n < 10:
            continue
        E = _l2n(np.stack([st[i].embedding for i in range(n)]))
        # semantic velocity: mean cosine distance between consecutive entries
        vel = float(np.mean([1.0 - float(E[i] @ E[i + 1]) for i in range(n - 1)]))
        # local semantic entropy: mean cosine distance to K_NN nearest neighbors
        nn = NearestNeighbors(n_neighbors=K_NN, metric="cosine").fit(E)
        d, _ = nn.kneighbors(E)
        local_ent = float(d[:, 1:].mean())
        # topic-switch rate: fraction of consecutive category changes
        cats = [st[i].category for i in range(n) if st[i].category is not None]
        switch = float(np.mean([1.0 for i in range(len(cats) - 1) if cats[i] != cats[i + 1]])) if len(cats) > 1 else float("nan")
        # forecast error for this subject (h=1)
        samples = build_horizon_samples(st, K, H)
        errs = [1.0 - protocol.cosine(model.predict(s, st), st[s.target_index].embedding) for s in samples]
        err = float(np.mean(errs)) if errs else float("nan")
        per_subj_entropy[sub] = {"velocity": round(vel, 4), "local_entropy": round(local_ent, 4),
                                  "topic_switch": round(switch, 4), "error": round(err, 4)}
        subj_err.append(err); subj_entropy.append(local_ent)
    vel_mean = float(np.mean([v["velocity"] for v in per_subj_entropy.values()]))
    ent_mean = float(np.mean([v["local_entropy"] for v in per_subj_entropy.values()]))
    sw_mean = float(np.nanmean([v["topic_switch"] for v in per_subj_entropy.values()]))
    ent_err_corr = _spearman(subj_entropy, subj_err)
    results["s41_entropy"] = {
        "mean_semantic_velocity": round(vel_mean, 4),
        "mean_local_semantic_entropy": round(ent_mean, 4),
        "mean_topic_switch_rate": round(sw_mean, 4),
        "local_entropy_vs_forecast_error_spearman": round(ent_err_corr, 4),
        "n_subjects": len(subj_err),
        "note": "higher local entropy -> worse forecasting? (spearman)",
    }

    # ---------- §43 local linearity: residual autocorrelation + local curvature ----------
    # Residuals (in embedding space) for train subjects; check autocorrelation of residual norm.
    resid_acf, curvatures = [], []
    for sub in train:
        st = states_by_sub[sub]
        n = len(st)
        if n < 12:
            continue
        samples = build_horizon_samples(st, K, H)
        rnorm = []
        for s in samples:
            pred = model.predict(s, st)
            resid = st[s.target_index].embedding - pred
            rnorm.append(float(np.linalg.norm(resid)))
        rnorm = np.asarray(rnorm)
        if len(rnorm) > 5:
            # autocorrelation at lag 1
            r = rnorm - rnorm.mean()
            acf1 = float(np.sum(r[:-1] * r[1:]) / (np.sum(r * r) + 1e-12))
            resid_acf.append(acf1)
        # local curvature: angle between consecutive segments (0 = straight/linear)
        E = np.stack([st[i].embedding for i in range(n)])
        for i in range(1, n - 1):
            v1 = E[i] - E[i - 1]
            v2 = E[i + 1] - E[i]
            c = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-12))
            curvatures.append(float(np.arccos(np.clip(c, -1, 1))))
    results["s43_local_linearity"] = {
        "residual_autocorr_lag1_mean": round(float(np.mean(resid_acf)), 4),
        "local_curvature_mean_rad": round(float(np.mean(curvatures)), 4),
        "local_curvature_median_rad": round(float(np.median(curvatures)), 4),
        "note": "residual ACF ~0 and low curvature => locally well-approximated by linear dynamics",
    }

    # ---------- §44 nonlinear residual test (k-NN on residuals, train-only) ----------
    # Build (history -> residual) for train; fit k-NN; evaluate residual prediction on test.
    tr_X, tr_R = [], []
    for s in tr_samples:
        st = states_by_sub[s.subject]
        x = np.concatenate([st[i].embedding for i in s.history])
        pred = model.predict(s, st)
        resid = st[s.target_index].embedding - pred
        tr_X.append(x); tr_R.append(resid)
    tr_X = np.asarray(tr_X); tr_R = np.asarray(tr_R)
    # test samples
    te_X, te_R = [], []
    for sub in test:
        st = states_by_sub[sub]
        for s in build_horizon_samples(st, K, H):
            x = np.concatenate([st[i].embedding for i in s.history])
            pred = model.predict(s, st)
            resid = st[s.target_index].embedding - pred
            te_X.append(x); te_R.append(resid)
    te_X = np.asarray(te_X); te_R = np.asarray(te_R)
    knn = NearestNeighbors(n_neighbors=5, metric="cosine").fit(tr_X)
    d, idx = knn.kneighbors(te_X)
    knn_pred = tr_R[idx].mean(axis=1)
    # residual predictability: cosine of (knn_pred, true residual) vs a null (random residual)
    obs_resid_cos = float(np.mean([protocol.cosine(p, r) for p, r in zip(knn_pred, te_R)]))
    rng = np.random.default_rng(SEED)
    null_cos = float(np.mean([protocol.cosine(tr_R[int(rng.integers(0, len(tr_R)))], r) for r in te_R]))
    results["s44_nonlinear_residual"] = {
        "knn_residual_cosine": round(obs_resid_cos, 4),
        "null_residual_cosine": round(null_cos, 4),
        "incremental_nonlinear_structure": bool(obs_resid_cos > null_cos + 0.01),
        "note": "if k-NN predicts residuals above the random-residual null, incremental nonlinear structure exists",
    }

    # ---------- §45 effective dimension ----------
    train_vecs = [states_by_sub[s][i].embedding for s in train for i in range(len(states_by_sub[s]))]
    train_E = _l2n(np.stack(train_vecs))
    # PCA participation ratio + explained variance
    mean = train_E.mean(axis=0)
    U, S, Vt = np.linalg.svd(train_E - mean, full_matrices=False)
    lam = (S ** 2) / (S ** 2).sum()
    participation_ratio = float((lam.sum() ** 2) / (lam ** 2).sum())
    explained_var_10 = float(lam[:10].sum())
    explained_var_20 = float(lam[:20].sum())
    # MLE intrinsic dimension (on a subsample for speed)
    rng = np.random.default_rng(SEED)
    idx_sub = rng.choice(len(train_E), size=min(2000, len(train_E)), replace=False)
    mle_dim = mle_intrinsic_dim(train_E[idx_sub], rng)
    results["s45_effective_dimension"] = {
        "pca_participation_ratio": round(participation_ratio, 2),
        "explained_variance_top10": round(explained_var_10, 4),
        "explained_variance_top20": round(explained_var_20, 4),
        "mle_intrinsic_dimension": round(mle_dim, 2),
        "ambient_dim": int(train_E.shape[1]),
    }

    # ---------- §46 dimension vs predictability (across subjects) ----------
    subj_dim, subj_acc = [], []
    for sub in subs:
        st = states_by_sub[sub]
        n = len(st)
        if n < 15:
            continue
        E = _l2n(np.stack([st[i].embedding for i in range(n)]))
        # per-subject participation ratio
        m = E.mean(axis=0)
        try:
            _, Sv, _ = np.linalg.svd(E - m, full_matrices=False)
            l = (Sv ** 2) / (Sv ** 2).sum()
            pr = float((l.sum() ** 2) / (l ** 2).sum())
        except Exception:
            continue
        samples = build_horizon_samples(st, K, H)
        acc = float(np.mean([protocol.cosine(model.predict(s, st), st[s.target_index].embedding) for s in samples]))
        subj_dim.append(pr); subj_acc.append(acc)
    dim_acc_corr = _spearman(subj_dim, subj_acc)
    results["s46_dimension_vs_predictability"] = {
        "dimension_vs_accuracy_spearman": round(dim_acc_corr, 4),
        "n_subjects": len(subj_dim),
        "note": "exploratory: higher-dimensional / more diffuse trajectories may be less predictable",
    }

    # ---------- §47 attractor-like structure ----------
    recurrence, dwell, persistence = [], [], []
    for sub in subs:
        st = states_by_sub[sub]
        n = len(st)
        if n < 20:
            continue
        E = _l2n(np.stack([st[i].embedding for i in range(n)]))
        # recurrence: fraction of pairs (i,j), j>i+1, with cosine > 0.8 (returns to a similar state)
        sim = E @ E.T
        np.fill_diagonal(sim, 0.0)
        above = np.sum(sim > 0.8) / 2
        recurrence.append(float(above) / (n * (n - 1) / 2))
        # dwell: mean run length where consecutive cosine > 0.8
        run, runs = 1, []
        for i in range(1, n):
            if float(E[i - 1] @ E[i]) > 0.8:
                run += 1
            else:
                runs.append(run); run = 1
        runs.append(run)
        dwell.append(float(np.mean(runs)))
        # state persistence: autocorrelation of the embedding at lag 5
        r = E - E.mean(axis=0)
        acf5 = float(np.sum(r[:-5] * r[5:], axis=1).mean() / (np.sum(r * r, axis=1).mean() + 1e-12))
        persistence.append(acf5)
    results["s47_attractor_like"] = {
        "mean_recurrence_frac": round(float(np.mean(recurrence)), 4),
        "mean_dwell_time": round(float(np.mean(dwell)), 3),
        "mean_state_persistence_lag5": round(float(np.mean(persistence)), 4),
        "note": "descriptive metastability; 'attractor-like' only if warranted, NOT neural attractors",
    }

    # ---------- Decision ----------
    # Descriptive; the object is the PREDICTION (history -> target), not the raw trajectory
    # curvature (which is high in 384-d space by construction). The linear model captures most
    # of the accessible predictive structure if: (a) residual autocorrelation is small, and
    # (b) the nonlinear residual is negligible (k-NN residual cosine near 0).
    small_acf = abs(results["s43_local_linearity"]["residual_autocorr_lag1_mean"]) < 0.2
    negligible_nonlinear = results["s44_nonlinear_residual"]["knn_residual_cosine"] < 0.05
    high_dynamics = (results["s41_entropy"]["mean_semantic_velocity"] > 0.5
                     and results["s47_attractor_like"]["mean_dwell_time"] < 2.0)
    if small_acf and negligible_nonlinear:
        decision = "CMDYN_LINEAR_PREDICTION_DOMINANT"
    elif small_acf:
        decision = "CMDYN_LINEAR_WITH_NONLINEAR_RESIDUAL"
    else:
        decision = "CMDYN_NONLINEAR_STRUCTURE"
    results["high_dynamics"] = bool(high_dynamics)
    results["decision"] = decision
    results["runtime_s"] = round(time.time() - t0, 1)

    (OUT / "cm_dynamics.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for k in ("s41_entropy", "s43_local_linearity", "s44_nonlinear_residual",
              "s45_effective_dimension", "s46_dimension_vs_predictability", "s47_attractor_like"):
        print(f"  {k}: {json.dumps(results[k])}")
    print(f"\n[dyn] DECISION: {decision}")
    print(f"[dyn] wrote {OUT / 'cm_dynamics.json'} in {results['runtime_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
