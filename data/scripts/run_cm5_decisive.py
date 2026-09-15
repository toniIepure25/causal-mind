#!/usr/bin/env python3
"""CM-5 Stage B: DECISIVE analysis (frozen protocol + CM5-ELIG-1 cohort).

For each frozen horizon h in {1,3,5,10}, per neural representation N1/N2/N3:
  - build HRF-safe, steady-state (AM-1: onset>=36s) samples (subject, t, h)
  - M0 = frozen CM-3 behavioral baseline (Ridge, last k=3 embeddings -> target)
  - M2 = behavior + nuisance ; M4 = behavior + nuisance + neural
  - IncrementalNeuralGain = M4 - M2, subject-disjoint (fit TRAIN, score TEST)
  - mandatory residual test (built into FusionModel)
  - destructive controls NC1-NC6
  - subject-level inference: mean gain, bootstrap CI, permutation p, effect size,
    proportion of test subjects with positive gain
Primary neural representation: N2 (Schaefer 400). N1/N3 = capacity ladder.
Sensitivity: S1 (strict motion screen), S2 (top-decile motion), S3 (per-horizon counts).

NO test-subject fitting. N3 PCA fit on TRAIN only. alpha frozen at 100 (CM-3).
"""
from __future__ import annotations
import json
import sys
import time
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/jovyan/work/causal-mind-v2/src")
from causal_mind.data import osf_a56rm
from causal_mind.thought import state_v1
from causal_mind.thought.encode import MiniLMEncoder
from causal_mind.neural.fusion import FusionModel, score_cosine, incremental_neural_gain
from causal_mind.neural.negative_controls import (
    SubjectSample, nc1_subject_permute, nc2_temporal_shift, nc3_block_permute,
    nc4_nuisance_only, nc5_neural_randomize, nc6_target_permute)
from causal_mind.eval.protocol import bootstrap_ci, cosine

ROOT = "/home/jovyan/work/causal-mind-v2"
FEAT = f"{ROOT}/data/derived/cm5_features"
SEAL = f"{ROOT}/reports/cm5_cohort_seal.json"
QC = f"{ROOT}/reports/cm5_qc_audit.tsv"
OUT = f"{ROOT}/reports/cm5_decisive_results.json"
SEED = 20260915
# Alignment-integrity exclusion (CM5-ALIGN-1): sub-036 has 2 OSF thoughts
# (4.79s, 65.51s) with no matching raw MRI events.tsv entry (raw starts at
# 84.13s) — the OSF<->MRI time-base equality is discrepant for this subject.
# Outcome-independent data-integrity exclusion (train subject).
ALIGN_EXCL = ("sub-036",)
HORIZONS = (1, 3, 5, 10)
K = 3
ALPHA = 100.0
TR = 1.5
B_S = 6.0
W_S = 15.0
N_NONSTEADY = 10
ONSET_MIN = 36.0          # AM-1 steady-state
SCAN = 600.0
N_PCA = 50
N_BOOT = 2000
N_PERM = 1000


def vol_indices(target_onset: float, n_vol: int) -> list[int]:
    """BOLD volume indices in [o-B-W, o-B]."""
    lo = target_onset - B_S - W_S
    hi = target_onset - B_S
    idx = [i for i in range(n_vol) if lo <= i * TR <= hi]
    # HRF-safe hard check: every volume strictly before onset
    assert all(i * TR < target_onset for i in idx), "HRF target contamination"
    assert all(i * TR <= hi for i in idx)
    return idx


def speech_features(ev_onset, ev_dur, ev_nw, w0, w1):
    """Speech/motor nuisance for window [w0, w1]. ALL features use only event
    information available at or before w1 (the prediction cutoff) — the lag-to-
    next-onset feature was removed because the next onset after the cutoff is
    the target's own onset (post-cutoff information)."""
    end = ev_onset + ev_dur
    # overlap of each event with the window
    ov = np.clip(np.minimum(end, w1) - np.maximum(ev_onset, w0), 0, None)
    utter_dur = float(ov.sum())
    words = float((ev_nw * (ov / np.clip(ev_dur, 1e-8, None))).sum())
    word_rate = words / max(w1 - w0, 1e-8)
    # silence before window: gap from last event ending before w0
    before = end[end < w0]
    silence = float(w0 - before.max()) if before.size else 30.0
    silence = min(silence, 30.0)
    return np.array([utter_dur, word_rate, silence], dtype=np.float32)


def _causal_zscore(ts, idx, cutoff):
    """Z-score the window `ts[idx]` using ONLY pre-cutoff statistics (causal,
    HRF-safe). Removes subject-specific baseline/scale so features generalize
    across subjects. ts: (T, F)."""
    c_vol = max(2, int(cutoff / TR))
    pre = ts[:min(c_vol, ts.shape[0])]
    mu = pre.mean(axis=0)
    sd = pre.std(axis=0) + 1e-8
    return (ts[idx] - mu) / sd


def build_subject_samples(sub, feat, states, pca):
    """All (t, h) samples for a subject across horizons. Returns dict h -> arrays."""
    n_vol = feat["n2"].shape[0]
    n2 = feat["n2"]; n1 = feat["n1"]; conf = feat["conf"]
    ev_o = feat["ev_onset"]; ev_d = feat["ev_dur"]; ev_nw = feat["ev_nw"]
    n = len(states)
    out = {}
    for h in HORIZONS:
        beh, nn1, nn2, nn3, nuis, tgt, onsets = [], [], [], [], [], [], []
        for t in range(K - 1, n - h):
            j = t + h
            o = states[j].onset
            if o < ONSET_MIN or o + states[j].duration > SCAN:
                continue
            idx = vol_indices(o, n_vol)
            if not idx:
                continue
            b = np.concatenate([states[i].embedding for i in range(t - K + 1, t + 1)])
            w0, w1 = o - B_S - W_S, o - B_S
            cutoff = o - B_S
            nn2w = _causal_zscore(n2, idx, cutoff).mean(axis=0)
            nn1w = _causal_zscore(n1, idx, cutoff).mean(axis=0)
            beh.append(b)
            nn1.append(nn1w)
            nn2.append(nn2w)
            nn3.append(pca.transform(nn2w.reshape(1, -1))[0])
            nuis.append(np.concatenate([conf[idx].mean(axis=0),
                                        speech_features(ev_o, ev_d, ev_nw, w0, w1)]))
            tgt.append(states[j].embedding)
            onsets.append(o)
        if beh:
            out[h] = dict(
                behavior=np.stack(beh), n1=np.stack(nn1), n2=np.stack(nn2),
                n3=np.stack(nn3), nuisance=np.stack(nuis), target=np.stack(tgt),
                onsets=np.array(onsets))
    return out


def subject_disjoint_gains(all_samples, train, test, neural_key, use_nuisance=True,
                           rng=None):
    """Fit on train, score each test subject. Returns per-test-subject (m0,m2,m4)."""
    tr = [s for s in train if s in all_samples]
    te = [s for s in test if s in all_samples]
    # pool train
    Xb = np.vstack([all_samples[s]["behavior"] for s in tr])
    Y = np.vstack([all_samples[s]["target"] for s in tr])
    Xn = np.vstack([all_samples[s][neural_key] for s in tr])
    Xg = np.vstack([all_samples[s]["nuisance"] for s in tr])
    m0 = FusionModel(alpha=ALPHA, use_neural=False, use_nuisance=False)
    m0.fit(Xb, Y)
    m2 = FusionModel(alpha=ALPHA, use_neural=False, use_nuisance=use_nuisance)
    m2.fit(Xb, Y, None, Xg)
    m4 = FusionModel(alpha=ALPHA, use_neural=True, use_nuisance=use_nuisance)
    m4.fit(Xb, Y, Xn, Xg)
    per_sub = {}
    for s in te:
        sb = all_samples[s]
        p0 = m0.predict(sb["behavior"])
        p2 = m2.predict(sb["behavior"], None, sb["nuisance"])
        p4 = m4.predict(sb["behavior"], sb[neural_key], sb["nuisance"])
        s0 = score_cosine(p0, sb["target"])
        s2 = score_cosine(p2, sb["target"])
        s4 = score_cosine(p4, sb["target"])
        per_sub[s] = (s0, s2, s4)
    return per_sub


def build_ss_list(flat, neural_key):
    return [SubjectSample(s, flat[s]["behavior"], flat[s][neural_key],
                           flat[s]["nuisance"], flat[s]["target"])
            for s in flat if s in flat]


def control_gain(ss_list, train, test, neural_key, use_nuisance=True, rng=None):
    """Recompute subject-disjoint M4-M2 gain on a (possibly controlled) SS list."""
    # rebuild flat arrays from the SS list
    flat = {d.subject: dict(behavior=d.behavior, target=d.target,
                            nuisance=d.nuisance, **{neural_key: d.neural})
            for d in ss_list}
    per_sub = subject_disjoint_gains(flat, train, test, neural_key, use_nuisance)
    agg = aggregate(per_sub)
    return agg["mean_gain"], agg


def aggregate(per_sub):
    """Subject-level inference on the M4-M2 gain."""
    gains = np.array([v[2] - v[1] for v in per_sub.values()])
    m0 = np.array([v[0] for v in per_sub.values()])
    m2 = np.array([v[1] for v in per_sub.values()])
    m4 = np.array([v[2] for v in per_sub.values()])
    ci = bootstrap_ci(gains, n_boot=N_BOOT, seed=SEED)
    # sign-flip permutation p: under H0 (no neural gain) the per-subject gain
    # distribution is symmetric around 0; flip signs to build the null.
    rng = np.random.default_rng(SEED)
    obs = gains.mean()
    cnt = 0
    for _ in range(N_PERM):
        signs = rng.choice(np.array([-1.0, 1.0]), size=gains.size)
        if (signs * gains).mean() >= obs:
            cnt += 1
    p = (cnt + 1) / (N_PERM + 1)
    # standardized effect size (Cohen's d vs 0)
    d = obs / (gains.std(ddof=1) + 1e-8)
    # bootstrap_ci returns (mean, lo, hi); the 95% CI is [lo, hi]
    return {
        "n_test_subjects": int(len(gains)),
        "mean_gain": float(obs),
        "ci95": [float(ci[1]), float(ci[2])],
        "permutation_p": float(p),
        "cohens_d": float(d),
        "prop_positive": float((gains > 0).mean()),
        "per_subject_gain": {k: float(v[2] - v[1]) for k, v in per_sub.items()},
        "m0_mean": float(m0.mean()), "m2_mean": float(m2.mean()), "m4_mean": float(m4.mean()),
    }


def main():
    t0 = time.time()
    seal = json.load(open(SEAL))
    train = seal["included_subjects"]["train"]
    val = seal["included_subjects"]["val"]
    test = seal["included_subjects"]["test"]

    # F2 gate: tSNR floor
    man = pd.read_csv(f"{ROOT}/reports/cm5_feature_manifest.tsv", sep="\t")
    man = man.set_index("subject")
    tsnr = man.loc[[s for s in train + val + test if s in man.index], "tsnr"]
    tsnr = tsnr.dropna()
    floor_abs = 2.0
    floor_pct = float(tsnr.quantile(0.05))
    f2_excl = sorted(set(tsnr[tsnr < max(floor_abs, floor_pct)].index))
    print(f"F2 tSNR: min={tsnr.min():.2f} p5={floor_pct:.2f} abs={floor_abs}; excluded={f2_excl}")
    # alignment-integrity exclusions (CM5-ALIGN-1)
    align_excl = [s for s in ALIGN_EXCL if s in set(train + val + test)]
    print(f"ALIGN exclusions (CM5-ALIGN-1): {align_excl}")
    excl = set(f2_excl) | set(align_excl)

    # load features + states
    enc = MiniLMEncoder()
    all_samples = {}
    tsnr_map = {}
    for sub in train + val + test:
        if sub in excl:
            continue
        feat = np.load(f"{FEAT}/{sub}.npz")
        tsnr_map[sub] = float(feat["tsnr"])
        events = osf_a56rm.load_thought_events(sub)
        states = state_v1.states_from_events(sub, events)
        state_v1.embed_states(states, enc)
        # N3 PCA placeholder; fitted below on train. Use identity-safe dummy first.
        all_samples[sub] = (feat, states)

    # Fit N3 PCA on TRAIN N2 window features (causal z-scored, matching prediction)
    train_n2 = []
    for sub in train:
        if sub in excl:
            continue
        feat, states = all_samples[sub]
        n_vol = feat["n2"].shape[0]
        for j, st in enumerate(states):
            o = st.onset
            if o < ONSET_MIN or o + st.duration > SCAN:
                continue
            idx = vol_indices(o, n_vol)
            if idx:
                train_n2.append(_causal_zscore(feat["n2"], idx, o - B_S).mean(axis=0))
    train_n2 = np.vstack(train_n2)
    from causal_mind.neural.features import TrainPCA
    pca = TrainPCA(n_components=N_PCA).fit(train_n2)
    print(f"N3 PCA fit on {train_n2.shape[0]} train window features -> {N_PCA} comps "
          f"({time.time()-t0:.0f}s)")

    # build samples (with PCA)
    samples_by_sub = {}
    for sub in train + val + test:
        if sub in excl:
            continue
        feat, states = all_samples[sub]
        samples_by_sub[sub] = build_subject_samples(sub, feat, states, pca)
    print(f"samples built for {len(samples_by_sub)} subjects ({time.time()-t0:.0f}s)")

    results = {
        "seed": SEED, "horizons": list(HORIZONS), "k": K, "alpha": ALPHA,
        "onset_min_s": ONSET_MIN, "n_pca": N_PCA,
        "f2_tsnr_excluded": f2_excl,
        "align_excluded": align_excl,
        "n_eligible": int(len(samples_by_sub)),
        "split": {"train": len(train), "val": len(val), "test": len(test)},
        "primary_neural": "N2",
        "per_horizon": {},
    }

    for h in HORIZONS:
        # restrict samples to this horizon
        hs = {s: {kk: v for kk, v in d.items() if kk == h} for s, d in samples_by_sub.items()}
        # flatten: each subject has one horizon dict
        flat = {}
        for s, d in hs.items():
            if h in d:
                flat[s] = d[h]
        res_h = {"n_samples_train": int(sum(flat[s]["behavior"].shape[0]
                                             for s in train if s in flat)),
                 "n_samples_test": int(sum(flat[s]["behavior"].shape[0]
                                           for s in test if s in flat)),
                 "n_test_subjects": int(sum(1 for s in test if s in flat))}
        for nkey, nname in (("n1", "N1"), ("n2", "N2"), ("n3", "N3")):
            per_sub = subject_disjoint_gains(flat, train, test, nkey)
            agg = aggregate(per_sub)
            res_h[nname] = agg
        # destructive negative controls on the PRIMARY representation (N2)
        rng = np.random.default_rng(SEED + h)
        ss = build_ss_list(flat, "n2")
        base_gain = res_h["N2"]["mean_gain"]
        res_h["N2"]["controls"] = {}
        for cname, cfn in (
                ("NC1_subject_perm", lambda d: nc1_subject_permute(d, rng)),
                ("NC2_temporal_shift", lambda d: nc2_temporal_shift(d, shift=7, rng=rng)),
                ("NC3_block_perm", lambda d: nc3_block_permute(d, block=4, rng=rng)),
                ("NC4_nuisance_only", lambda d: nc4_nuisance_only(d)),
                ("NC5_neural_randomize", lambda d: nc5_neural_randomize(d, rng)),
                ("NC6_target_perm", lambda d: nc6_target_permute(d, rng))):
            ctl = cfn(ss)
            g, _ = control_gain(ctl, train, test, "n2", rng=rng)
            res_h["N2"]["controls"][cname] = {
                "mean_gain": float(g), "collapsed": bool(abs(g) < abs(base_gain) / 2)}
        results["per_horizon"][h] = res_h
        print(f"h={h}: N2 gain={res_h['N2']['mean_gain']:.4f} "
              f"ci={res_h['N2']['ci95']} p={res_h['N2']['permutation_p']:.3f} "
              f"prop+={res_h['N2']['prop_positive']:.2f} ({time.time()-t0:.0f}s)", flush=True)

    # ---- Sensitivity analyses (secondary) on the primary N2, all horizons ----
    qc = pd.read_csv(QC, sep="\t").set_index("subject_id")
    results["sensitivity"] = {}
    for sname, pred in (
            ("S1_strict_motion", lambda s: (qc.loc[s, "fd_mean"] > 0.3)
             or (qc.loc[s, "fd_gt05_frac"] > 0.10)),
            ("S2_top_decile_motion", lambda s: qc.loc[s, "fd_mean"]
             > qc["fd_mean"].quantile(0.9))):
        drop = [s for s in train + val + test
                if s in qc.index and pred(s) and s in samples_by_sub]
        tr2 = [s for s in train if s not in drop]
        te2 = [s for s in test if s not in drop]
        sres = {"n_dropped": len(drop), "dropped": drop, "per_horizon": {}}
        for h in HORIZONS:
            flat = {s: d[h] for s, d in samples_by_sub.items() if h in d}
            per_sub = subject_disjoint_gains(flat, tr2, te2, "n2")
            agg = aggregate(per_sub)
            sres["per_horizon"][h] = {"mean_gain": agg["mean_gain"],
                                      "ci95": agg["ci95"],
                                      "prop_positive": agg["prop_positive"]}
        results["sensitivity"][sname] = sres
        print(f"{sname}: dropped {len(drop)}; "
              + ", ".join(f"h{h}={sres['per_horizon'][h]['mean_gain']:.4f}"
                          for h in HORIZONS), flush=True)
    # S3: per-horizon valid-instance counts per subject (primary cohort)
    s3 = {}
    for h in HORIZONS:
        counts = {s: int(samples_by_sub[s][h]["behavior"].shape[0])
                  for s in samples_by_sub if h in samples_by_sub[s]}
        s3[h] = {"min": min(counts.values()), "median": int(np.median(list(counts.values()))),
                 "max": max(counts.values()),
                 "n_subjects_with_<10": int(sum(1 for v in counts.values() if v < 10))}
    results["sensitivity"]["S3_per_horizon_counts"] = s3

    json.dump(results, open(OUT, "w"), indent=2)
    print(f"wrote {OUT} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
