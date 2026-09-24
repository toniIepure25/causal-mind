"""CM-LAB §36-40: Personalization (prospective only) + predictability reliability.

Scientific question (§36): does a small amount of a person's OWN earlier thought history
improve prediction of their LATER thoughts?

Strict chronology (no leakage):
  * GLOBAL (P0): model fit on TRAIN (without the target subject).
  * PERSONALIZED: same global model + lightweight adaptation using ONLY the target
    subject's EARLIER observations (EARLY segment).
  * Evaluation: the target subject's LATER observations (LATE segment, held out).

Personalization ladder (§37, simple first):
  P0 global model.
  P1 global + subject-specific intercept (mean residual on adaptation data).
  P3 global + subject-specific ridge residual correction (ridge: global_pred -> residual).

Data curve (§38): adaptation gain vs fraction of EARLY data used (0/10/25/50%).
Failure modes (§39): overfitting at high adaptation fractions, low-data subjects.
Reliability (§40): session-level predictability stability (first-half vs second-half).

Decision: CMPERS_GAIN / CMPERS_SMALL_GAIN / CMPERS_NULL / CMPERS_OVERFIT.

Usage:
    .venv/bin/python data/scripts/cm_personalization.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge

from causal_mind.data import osf_a56rm
from causal_mind.eval import protocol
from causal_mind.eval.protocol import bootstrap_ci
from causal_mind.forecast.multihorizon_model import LinearMultiHorizon
from causal_mind.thought import state_v1
from causal_mind.thought.multihorizon import build_horizon_samples

ROOT = Path("/home/jovyan/work/causal-mind-v2")
OUT = ROOT / "reports" / "cm_personalization"
EMB_CACHE = Path("/home/jovyan/work/xval_scratch/ds006067_embeddings.npz")
SEED = 20260911
K = 3
H = 1
ALPHA = 100.0
FRACTIONS = (0.0, 0.1, 0.25, 0.5)


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
    raise RuntimeError("embedding cache missing; run cm_uncertainty.py first to build it")


def _err(preds, actuals):
    return float(np.mean([1.0 - protocol.cosine(p, a) for p, a in zip(preds, actuals)]))


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    states_by_sub, subs = load_states()
    split = protocol.subject_disjoint_split(subs, seed=SEED)
    assert protocol.verify_seal(split, SEED, len(subs)), "CM-2 SEAL MISMATCH"
    train, val, test = list(split.train), list(split.val), list(split.test)
    print(f"[pers] {len(subs)} subjects; split {len(train)}/{len(val)}/{len(test)}; seal OK")

    # Global model fit on TRAIN (without any test subject).
    tr_samples = [s for s in train for s in build_horizon_samples(states_by_sub[s], K, H)]
    model = LinearMultiHorizon(k=K, alpha=ALPHA, horizons=(H,))
    model.fit({H: tr_samples}, states_by_sub)

    results: dict = {
        "protocol": "CM-LAB S36-40 personalization (prospective) + reliability",
        "dataset": "ds006067 thought-stream", "seed": SEED, "k": K, "h": H,
        "split": {"train": len(train), "val": len(val), "test": len(test)},
        "fractions": list(FRACTIONS),
        "mean_p0_error": None,
    }

    # Per-subject personalization.
    per_subj = []
    for sub in test:
        st = states_by_sub[sub]
        n = len(st)
        if n < 8:
            continue
        mid = n // 2
        all_samples = build_horizon_samples(st, K, H)
        late = [s for s in all_samples if s.target_index >= mid]
        early = [s for s in all_samples if s.target_index < mid]
        if len(late) < 3 or len(early) < 3:
            continue
        # Global predictions on LATE.
        late_pred0 = [model.predict(s, st) for s in late]
        late_act = [st[s.target_index].embedding for s in late]
        err_p0 = _err(late_pred0, late_act)
        # Global predictions on EARLY (for adaptation).
        early_pred0 = [model.predict(s, st) for s in early]
        early_act = [st[s.target_index].embedding for s in early]

        subj = {"subject": sub, "n": n, "n_late": len(late), "n_early": len(early),
                "err_p0": round(err_p0, 4), "gains": {}}
        for f in FRACTIONS:
            n_adapt = int(round(f * len(early)))
            if n_adapt == 0:
                # P0 (no adaptation)
                subj["gains"]["P1_f0.0"] = 0.0
                subj["gains"]["P3_f0.0"] = 0.0
                continue
            adapt = early[:n_adapt]
            adapt_pred = [early_pred0[i] for i in range(n_adapt)]
            adapt_act = [early_act[i] for i in range(n_adapt)]
            # P1: subject intercept = mean residual on adaptation data.
            resid = np.stack([a - p for p, a in zip(adapt_pred, adapt_act)])
            intercept = resid.mean(axis=0)
            p1_pred = [p + intercept for p in late_pred0]
            err_p1 = _err(p1_pred, late_act)
            # P3: ridge residual correction (global_pred -> residual), fit on adaptation.
            X = np.stack(adapt_pred)
            Y = np.stack([a - p for p, a in zip(adapt_pred, adapt_act)])
            ridge = Ridge(alpha=10.0).fit(X, Y)
            p3_pred = [p + ridge.predict(p.reshape(1, -1))[0] for p in late_pred0]
            err_p3 = _err(p3_pred, late_act)
            subj["gains"][f"P1_f{f}"] = round(err_p0 - err_p1, 4)
            subj["gains"][f"P3_f{f}"] = round(err_p0 - err_p3, 4)
        per_subj.append(subj)

    n_subj = len(per_subj)
    print(f"[pers] {n_subj} test subjects with usable early/late segments")

    # Verify: mean P0 error vs mean personalized error (to sanity-check the negative gain).
    mean_p0 = float(np.mean([s["err_p0"] for s in per_subj]))
    results["mean_p0_error"] = round(mean_p0, 4)
    for f in FRACTIONS:
        if f == 0.0:
            continue
        # recompute mean personalized error for this fraction (P1 = P3 here)
        errs = []
        for s in per_subj:
            errs.append(s["err_p0"] - s["gains"][f"P1_f{f}"])
        results[f"mean_p1_error_f{f}"] = round(float(np.mean(errs)), 4)
    print(f"[pers] mean P0 error = {mean_p0:.4f}")

    # Aggregate gains per level/fraction.
    levels = {}
    for key in per_subj[0]["gains"]:
        vals = np.array([s["gains"][key] for s in per_subj])
        ci = list(bootstrap_ci(vals, n_boot=2000, seed=SEED))
        levels[key] = {"mean_gain": round(float(vals.mean()), 4),
                        "ci95": [round(ci[1], 4), round(ci[2], 4)],
                        "proportion_positive": round(float(np.mean(vals > 0)), 3),
                        "n": int(n_subj)}
    results["levels"] = levels

    # Data curve (P3, the strongest adapter) by fraction.
    data_curve = {}
    for f in FRACTIONS:
        key = f"P3_f{f}"
        if key in levels:
            data_curve[f"{f}"] = levels[key]
    results["data_curve_P3"] = data_curve

    # Failure modes (§39): overfitting = gain turns negative at high fraction.
    p3_f05 = levels.get("P3_f0.5", {}).get("mean_gain", 0.0)
    p3_f01 = levels.get("P3_f0.1", {}).get("mean_gain", 0.0)
    overfit = p3_f05 < 0 and p3_f01 > 0
    # low-data subjects: gain for subjects with few early samples
    low_data = [s for s in per_subj if s["n_early"] < 10]
    low_data_gain = float(np.mean([s["gains"]["P3_f0.5"] for s in low_data])) if low_data else float("nan")
    results["failure_modes"] = {
        "overfitting_at_high_fraction": bool(overfit),
        "p3_gain_f0.1": p3_f01, "p3_gain_f0.5": p3_f05,
        "n_low_data_subjects": len(low_data),
        "low_data_p3_gain_f0.5": round(low_data_gain, 4),
    }

    # Reliability (§40): session-level predictability stability.
    # Per subject: error in first-half vs second-half of the LATE segment.
    first_half_err, second_half_err = [], []
    for sub in test:
        st = states_by_sub[sub]
        n = len(st)
        if n < 8:
            continue
        mid = n // 2
        late = [s for s in build_horizon_samples(st, K, H) if s.target_index >= mid]
        if len(late) < 6:
            continue
        half = len(late) // 2
        e1 = _err([model.predict(s, st) for s in late[:half]], [st[s.target_index].embedding for s in late[:half]])
        e2 = _err([model.predict(s, st) for s in late[half:]], [st[s.target_index].embedding for s in late[half:]])
        first_half_err.append(e1)
        second_half_err.append(e2)
    fh = np.asarray(first_half_err); sh = np.asarray(second_half_err)
    rel_pearson = float(np.corrcoef(fh, sh)[0, 1])
    # rank stability (Spearman)
    def _rank(a):
        o = a.argsort(); r = np.empty_like(o, dtype=float); r[o] = np.arange(len(a)); return r
    sp = float(np.corrcoef(_rank(fh), _rank(sh))[0, 1])
    results["reliability"] = {
        "n_subjects": int(len(fh)),
        "first_vs_second_half_pearson": round(rel_pearson, 4),
        "first_vs_second_half_spearman": round(sp, 4),
        "note": "session-level predictability stability (NOT a cognitive trait)",
    }

    # Decision (§39).
    p3_best = max((levels[f"P3_f{f}"]["mean_gain"] for f in FRACTIONS if f > 0), default=0.0)
    p1_best = max((levels[f"P1_f{f}"]["mean_gain"] for f in FRACTIONS if f > 0), default=0.0)
    best_gain = max(p3_best, p1_best)
    if overfit:
        decision = "CMPERS_OVERFIT"
    elif best_gain >= 0.01:
        decision = "CMPERS_GAIN"
    elif best_gain >= 0.003:
        decision = "CMPERS_SMALL_GAIN"
    else:
        decision = "CMPERS_NULL"
    results["decision"] = decision
    results["runtime_s"] = round(time.time() - t0, 1)

    (OUT / "cm_personalization.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print("\n[pers] P1 gains: " + ", ".join(f"f{f}={levels[f'P1_f{f}']['mean_gain']:+.4f}" for f in FRACTIONS if f > 0))
    print("[pers] P3 gains: " + ", ".join(f"f{f}={levels[f'P3_f{f}']['mean_gain']:+.4f}" for f in FRACTIONS if f > 0))
    print(f"[pers] reliability: pearson={rel_pearson:.3f} spearman={sp:.3f}")
    print(f"[pers] DECISION: {decision}")
    print(f"[pers] wrote {OUT / 'cm_personalization.json'} in {results['runtime_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
