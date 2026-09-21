"""CM-XVAL first milestone: external validation of the CM-2/CM-3 predictive-dynamics
finding on an EXTERNAL public dataset (Open Play, Ballou 2025; openESM 0075).

Finding under test (C-003/C-004, validated on ds006067):
    Given the frozen MiniLM embeddings of a subject's k most recent free-text entries,
    one predicts the SEMANTIC CONTENT (cosine) of the subject's next entry,
    out-of-sample with a subject-disjoint split, ABOVE the strongest frozen baseline.

External dataset:
    Open Play (digital-wellbeing/open-play), Zenodo DOI 10.5281/zenodo.17536656,
    CC-licensed. 1284 participants x 30 daily waves. We use the free-text
    `displaced_activity` field ("describe what you did instead of gaming") as the
    thought-analogue text stream. This is a genuine DOMAIN SHIFT (gaming-diary
    activity descriptions, not internal thoughts) -- exactly what an external
    validation should test: does temporal semantic persistence generalize beyond
    rich thought-streams?

Protocol (faithful transfer of CM-3, data/scripts/run_cm3_evaluation.py):
    * subject-disjoint 70/15/15 split (fresh seed 20260921; does NOT touch the
      frozen CM-2 seal);
    * per horizon h in (1,2,3,5,10): fit LinearMultiHorizon on TRAIN, select the
      strongest baseline B0-B7 on VAL, evaluate model + baseline on sealed TEST;
    * metric: per-subject mean cosine of predicted vs actual target embedding;
    * PredictiveGain(h) = Model(h) - StrongBaseline(h) with subject-level bootstrap CI;
    * target-shuffle permutation test on the primary horizon (h=1).

Decision states (new claim C-101; never reuses C-003/C-004):
    CMXVAL_PASS_REPLICATION / CMXVAL_PARTIAL / CMXVAL_NULL_NO_REPLICATION /
    CMXVAL_INCOMPATIBLE_DATASET.

Usage:
    .venv/bin/python data/scripts/cm_xval_openplay.py            # full
    .venv/bin/python data/scripts/cm_xval_openplay.py --quick    # fewer perms/horizons
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from causal_mind.eval import protocol
from causal_mind.eval.protocol import bootstrap_ci
from causal_mind.forecast import baselines_h
from causal_mind.forecast.multihorizon_model import LinearMultiHorizon
from causal_mind.thought import encode, state_v1
from causal_mind.thought.multihorizon import (
    all_samples_leakage_free,
    build_horizon_samples,
)

ROOT = Path("/home/jovyan/work/causal-mind-v2")
DATA = Path("/home/jovyan/work/xval_scratch/survey_daily.csv.gz")
OUT = ROOT / "reports" / "cm_xval"
SEED = 20260921
K = 3
HORIZONS = (1, 2, 3, 5, 10)
PRIMARY_H = 1
MIN_ENTRIES = 5
B_PERM = 1000
ALPHA = 100.0

SOURCE = {
    "name": "Open Play (digital-wellbeing/open-play)",
    "openesm_id": "0075_ballou",
    "zenodo_doi": "10.5281/zenodo.17536656",
    "url": "https://github.com/digital-wellbeing/open-play",
    "field": "displaced_activity",
    "license": "CC (see repo)",
    "note": "gaming-diary free-text activity descriptions; domain shift from thoughts",
}


def load_states(min_entries: int) -> tuple[dict[str, list], dict]:
    df = pd.read_csv(DATA)
    txt = df["displaced_activity"].astype("string").str.strip()
    bad = {"", "na", "n/a", "none", "no", "null", "nan"}
    df = df[txt.notna() & ~txt.str.lower().isin(bad) & (txt.str.len() > 0)].copy()
    df = df.sort_values(["pid", "wave"])
    states_by_sub: dict[str, list] = {}
    for pid, g in df.groupby("pid", sort=False):
        rows = g.to_dict("records")
        if len(rows) < min_entries:
            continue
        sts = [
            state_v1.ThoughtState(
                subject=str(pid), index=i, onset=float(r["wave"]), duration=1.0,
                transcript=str(r["displaced_activity"]).strip(),
            )
            for i, r in enumerate(rows)
        ]
        states_by_sub[str(pid)] = sts
    n_entries = sum(len(v) for v in states_by_sub.values())
    return states_by_sub, {
        "n_subjects_total": int(df["pid"].nunique()),
        "n_subjects_used": len(states_by_sub),
        "n_entries": int(n_entries),
        "min_entries": min_entries,
        "entries_per_subject": {
            "mean": round(float(np.mean([len(v) for v in states_by_sub.values()])), 2),
            "median": float(np.median([len(v) for v in states_by_sub.values()])),
            "max": int(max(len(v) for v in states_by_sub.values())),
        },
    }


def _eval_semantic(predict, states_by_sub, subjects, k, h, corpus, c1):
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


def main() -> int:
    t0 = time.time()
    quick = "--quick" in sys.argv
    horizons = (1, 2, 5) if quick else HORIZONS
    b_perm = 200 if quick else B_PERM

    OUT.mkdir(parents=True, exist_ok=True)
    states_by_sub, data_info = load_states(MIN_ENTRIES)
    subjects = sorted(states_by_sub)
    print(f"[xval] {len(subjects)} subjects, {data_info['n_entries']} entries "
          f"(min_entries={MIN_ENTRIES})")

    # Embed all entries in one batch (frozen MiniLM).
    enc = encode.MiniLMEncoder()
    all_texts, all_idx = [], []
    for sub in subjects:
        for i, st in enumerate(states_by_sub[sub]):
            all_texts.append(st.transcript)
            all_idx.append((sub, i))
    print(f"[xval] embedding {len(all_texts)} entries ...")
    vecs = enc.encode(all_texts)
    for (sub, i), v in zip(all_idx, vecs):
        states_by_sub[sub][i].embedding = v

    # Subject-disjoint split (fresh seed; does NOT touch the frozen CM-2 seal).
    split = protocol.subject_disjoint_split(subjects, seed=SEED)
    train, val, test = list(split.train), list(split.val), list(split.test)
    # Leakage audit on the primary horizon.
    for sub in test[:5]:
        all_samples_leakage_free(build_horizon_samples(states_by_sub[sub], K, PRIMARY_H),
                                 {sub: states_by_sub[sub]})
    print(f"[xval] split {len(train)}/{len(val)}/{len(test)} (seed {SEED}); leakage OK")

    km = state_v1.fit_categories(
        [st for s in train for st in states_by_sub[s]], n_clusters=16, seed=SEED)
    for s in subjects:
        state_v1.assign_categories(states_by_sub[s], km)

    results: dict = {
        "protocol": "CM-3 transfer (subject-disjoint, k-history, horizon prediction)",
        "source": SOURCE, "seed": SEED, "k": K, "horizons": list(horizons),
        "data": data_info, "split": {"train": len(train), "val": len(val), "test": len(test)},
    }

    fpc = {}
    for h in horizons:
        corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, h, K)
        c1 = baselines_h.HorizonCorpus.build(states_by_sub, train, 1, K)
        bl = baselines_h.baselines_for(corpus, c1)
        tr_samples = {h: [s for s in train for s in build_horizon_samples(states_by_sub[s], K, h)]}
        model = LinearMultiHorizon(k=K, alpha=ALPHA, horizons=(h,))
        model.fit(tr_samples, states_by_sub)
        model_pred = lambda s, st, cc, cc1, _m=model: _m.predict(s, st)  # noqa: E731

        val_scores = {
            name: float(np.mean(_eval_semantic(lambda s, st, cc, cc1, fn=fn: fn(s, st, cc),
                                               states_by_sub, val, K, h, corpus, c1)))
            for name, fn in bl.items()
        }
        strong = max(val_scores, key=val_scores.get)
        strong_fn = bl[strong]
        m_test = _eval_semantic(model_pred, states_by_sub, test, K, h, corpus, c1)
        b_test = _eval_semantic(lambda s, st, cc, cc1, _f=strong_fn: _f(s, st, cc),
                                states_by_sub, test, K, h, corpus, c1)
        m_ci = list(bootstrap_ci(np.asarray(m_test), n_boot=2000, seed=SEED))
        b_ci = list(bootstrap_ci(np.asarray(b_test), n_boot=2000, seed=SEED))
        gain_ci = list(bootstrap_ci(np.asarray(m_test) - np.asarray(b_test),
                                    n_boot=2000, seed=SEED))
        fpc[h] = {
            "model_ci": m_ci, "strong_baseline": strong, "strong_baseline_ci": b_ci,
            "gain_ci": gain_ci, "val_baseline_scores": {k2: round(v2, 4) for k2, v2 in val_scores.items()},
            "n_test_subjects": len(m_test),
        }
        print(f"  h={h:2d}: model={m_ci[0]:.4f} vs {strong}={b_ci[0]:.4f} "
              f"gain={gain_ci[0]:+.4f} [{gain_ci[1]:+.4f},{gain_ci[2]:+.4f}]")
    results["FPC_semantic"] = fpc

    # Target-shuffle permutation test on the primary horizon.
    h = PRIMARY_H
    corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, h, K)
    model = LinearMultiHorizon(k=K, alpha=ALPHA, horizons=(h,))
    model.fit({h: [s for s in train for s in build_horizon_samples(states_by_sub[s], K, h)]},
              states_by_sub)
    test_samples = [(sub, s) for sub in test for s in build_horizon_samples(states_by_sub[sub], K, h)]
    rng = np.random.default_rng(SEED)
    obs = np.mean([protocol.cosine(model.predict(s, states_by_sub[sub]),
                                   states_by_sub[sub][s.target_index].embedding)
                   for sub, s in test_samples])
    null = np.empty(b_perm)
    for b in range(b_perm):
        tot = 0.0
        cnt = 0
        for sub, s in test_samples:
            st = states_by_sub[sub]
            j = int(rng.integers(0, len(st)))
            tot += protocol.cosine(model.predict(s, st), st[j].embedding)
            cnt += 1
        null[b] = tot / max(cnt, 1)
    p_perm = float((np.sum(null >= obs) + 1) / (b_perm + 1))
    results["permutation_primary_h"] = {
        "h": h, "observed_test_cosine": round(float(obs), 4),
        "null_mean": round(float(null.mean()), 4), "null_sd": round(float(null.std()), 4),
        "p": round(p_perm, 4), "B": b_perm,
    }
    print(f"  perm h={h}: obs={obs:.4f} null={null.mean():.4f} p={p_perm:.4f}")

    # Decision.
    g = fpc[h]["gain_ci"]
    gain_pos = g[0] > 0
    gain_ci_excl_zero = g[1] > 0
    if gain_ci_excl_zero and p_perm < 0.05:
        decision = "CMXVAL_PASS_REPLICATION"
    elif gain_pos and (g[2] > 0):
        decision = "CMXVAL_PARTIAL"
    else:
        decision = "CMXVAL_NULL_NO_REPLICATION"
    results["decision"] = decision
    results["runtime_s"] = round(time.time() - t0, 1)

    (OUT / "cm_xval_openplay.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\n[xval] DECISION: {decision}")
    print(f"[xval] wrote {OUT / 'cm_xval_openplay.json'} in {results['runtime_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
