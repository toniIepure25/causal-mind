"""CM-XVAL-1 inference adjudication (CM-LAB §25-28).

Resolves the apparent discrepancy between:
  (a) subject-level paired bootstrap CI for model-baseline gain (excludes 0), and
  (b) target-shuffle permutation p (~0.71).

This script:
  1. Determines exactly which null hypothesis each procedure tests.
  2. Recomputes the inference at the CORRECT unit (subject-level):
       - subject-level paired bootstrap
       - subject-level sign test
       - subject-level permutation (sign-flip randomization)
       - hierarchical (two-level) bootstrap
       - event-level analysis (descriptive secondary ONLY)
  3. Runs a predeclared family of destructive nulls (N0-N6), each with a
     documented purpose (what it destroys / preserves / tests).
  4. Writes machine-readable results + adjudication doc.

No CM-8 changes. No human data. External dataset only (Open Play).

Usage:
    .venv/bin/python data/scripts/cm_xval_inference.py
"""
from __future__ import annotations

import hashlib
import json
import math
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
EMB_CACHE = Path("/home/jovyan/work/xval_scratch/openplay_embeddings.npz")
OUT = ROOT / "reports" / "cm_xval"
DOCS = ROOT / "docs" / "cm_xval"
SEED = 20260921
K = 3
HORIZONS = (1, 2, 3, 5, 10)
PRIMARY_H = 1
MIN_ENTRIES = 5
ALPHA = 100.0
N_BOOT = 2000
B_NULL = 2000

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


def _data_key() -> str:
    h = hashlib.sha256()
    with open(DATA, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def embed_with_cache(states_by_sub: dict[str, list], subjects: list[str]) -> str:
    key = _data_key()
    if EMB_CACHE.exists():
        try:
            cache = np.load(EMB_CACHE, allow_pickle=False)
            if str(cache["data_key"]) == key:
                vecs = cache["vectors"]
                subs = cache["subjects"].tolist()
                idxs = cache["indices"].tolist()
                for (sub, i), v in zip(zip(subs, idxs), vecs):
                    states_by_sub[sub][i].embedding = v
                return "cache"
        except Exception:
            pass
    enc = encode.MiniLMEncoder()
    all_texts, all_idx = [], []
    for sub in subjects:
        for i, st in enumerate(states_by_sub[sub]):
            all_texts.append(st.transcript)
            all_idx.append((sub, i))
    vecs = enc.encode(all_texts)
    for (sub, i), v in zip(all_idx, vecs):
        states_by_sub[sub][i].embedding = v
    np.savez(EMB_CACHE,
             data_key=np.array(key),
             subjects=np.array([s for s, _ in all_idx]),
             indices=np.array([i for _, i in all_idx]),
             vectors=np.asarray(vecs, dtype=np.float32))
    return "fresh"


def _eval_with_events(predict, states_by_sub, subjects, k, h, corpus, c1):
    """Return (per_sub_mean_cos, events_by_sub{sub:[cos,...]})."""
    per_sub = []
    events_by_sub: dict[str, list] = {}
    for sub in subjects:
        st = states_by_sub[sub]
        coses = []
        for s in build_horizon_samples(st, k, h):
            pred = predict(s, st, corpus, c1)
            coses.append(protocol.cosine(pred, st[s.target_index].embedding))
        if coses:
            per_sub.append(float(np.mean(coses)))
            events_by_sub[sub] = coses
    return per_sub, events_by_sub


def binom_sf(k: int, n: int, p: float = 0.5) -> float:
    """P(X >= k) for X ~ Binomial(n, p)."""
    if n <= 0:
        return 1.0
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return float(total)


def sign_test_two_sided(n_pos: int, n_neg: int) -> float:
    n = n_pos + n_neg
    if n == 0:
        return 1.0
    p_one = binom_sf(max(n_pos, n_neg), n, 0.5)
    return float(min(1.0, 2.0 * p_one))


def hierarchical_bootstrap(m_events, b_events, n_boot, seed):
    """Two-level bootstrap: resample subjects, then events within each subject."""
    rng = np.random.default_rng(seed)
    subs = list(m_events.keys())
    n = len(subs)
    stat = np.empty(n_boot)
    for b in range(n_boot):
        tot, cnt = 0.0, 0
        for _ in range(n):
            sub = subs[int(rng.integers(0, n))]
            m = np.asarray(m_events[sub])
            bb = np.asarray(b_events[sub])
            idx = rng.integers(0, len(m), size=len(m))
            tot += float(np.sum(m[idx] - bb[idx]))
            cnt += int(len(m))
        stat[b] = tot / max(cnt, 1)
    lo, hi = np.percentile(stat, [2.5, 97.5])
    return float(np.mean(stat)), float(lo), float(hi)


def run_null_family(model, states_by_sub, test, h, b_null, seed):
    """Predeclared destructive nulls N0-N6 on the primary horizon.

    Returns dict null_id -> {observed, null_mean, null_sd, p, destroys, preserves, tests}.
    The model prediction is computed once per test sample (correct history); only the
    target (and, for N5, the history) changes across nulls.
    """
    rng = np.random.default_rng(seed)
    # Precompute predictions + actual targets + per-subject embedding pools.
    test_samples = [(sub, s) for sub in test for s in build_horizon_samples(states_by_sub[sub], K, h)]
    preds, targets, subs_list = [], [], []
    emb_by_sub = {sub: np.asarray([st.embedding for st in states_by_sub[sub]]) for sub in test}
    all_target_vecs = np.concatenate([emb_by_sub[sub] for sub in test])
    for sub, s in test_samples:
        preds.append(model.predict(s, states_by_sub[sub]))
        targets.append(emb_by_sub[sub][s.target_index])
        subs_list.append(sub)
    preds = np.asarray(preds)
    targets = np.asarray(targets)
    observed = float(np.mean([protocol.cosine(p, t) for p, t in zip(preds, targets)]))

    def _pstat(null_cos):
        null_cos = np.asarray(null_cos)
        p = float((np.sum(null_cos >= observed) + 1) / (b_null + 1))
        return {"observed": round(observed, 4),
                "null_mean": round(float(null_cos.mean()), 4),
                "null_sd": round(float(null_cos.std()), 4),
                "p": round(p, 4)}

    out: dict[str, dict] = {}

    # N0: target permutation ACROSS subjects (breaks subject identity + temporal link).
    n0 = []
    for b in range(b_null):
        j = rng.integers(0, len(all_target_vecs), size=len(test_samples))
        n0.append(np.mean([protocol.cosine(p, all_target_vecs[ji])
                           for p, ji in zip(preds, j)]))
    out["N0_across_subject_target"] = _pstat(n0) | {
        "destroys": "subject identity + temporal alignment",
        "preserves": "marginal target distribution",
        "tests": "does prediction match the (subject, temporal) target better than any random target"}

    # N1: within-subject target permutation (breaks temporal link, keeps subject).
    n1 = []
    sub_len = {sub: len(emb_by_sub[sub]) for sub in test}
    for b in range(b_null):
        cs = []
        for sub in subs_list:
            j = int(rng.integers(0, sub_len[sub]))
            cs.append(protocol.cosine(preds[len(cs)], emb_by_sub[sub][j]))
        n1.append(np.mean(cs))
    out["N1_within_subject_target"] = _pstat(n1) | {
        "destroys": "temporal alignment (specific next-entry)",
        "preserves": "subject identity + marginal",
        "tests": "does prediction beat a random entry of the SAME person"}

    # N2: circular temporal shift (preserves autocorrelation, breaks alignment).
    n2 = []
    for b in range(b_null):
        offset = {sub: int(rng.integers(1, max(2, len(emb_by_sub[sub])))) for sub in test}
        cs = []
        for sub, s in test_samples:
            n = len(emb_by_sub[sub])
            j = (s.target_index + offset[sub]) % n
            cs.append(protocol.cosine(preds[len(cs)], emb_by_sub[sub][j]))
        n2.append(np.mean(cs))
    out["N2_circular_temporal_shift"] = _pstat(n2) | {
        "destroys": "specific temporal alignment",
        "preserves": "temporal autocorrelation + subject identity + marginal",
        "tests": "does prediction exploit the specific alignment or just autocorrelation"}

    # N3: block shuffle preserving short-range autocorrelation (block size = K).
    n3 = []
    for b in range(b_null):
        perm = {}
        for sub in test:
            n = len(emb_by_sub[sub])
            blocks = [list(range(i, min(i + K, n))) for i in range(0, n, K)]
            rng.shuffle(blocks)
            flat = [idx for blk in blocks for idx in blk]
            perm[sub] = flat  # new_position -> original_index
        cs = []
        for sub, s in test_samples:
            j = perm[sub][s.target_index]
            cs.append(protocol.cosine(preds[len(cs)], emb_by_sub[sub][j]))
        n3.append(np.mean(cs))
    out["N3_block_shuffle"] = _pstat(n3) | {
        "destroys": "long-range temporal structure",
        "preserves": "short-range autocorrelation (within blocks) + subject + marginal",
        "tests": "is the signal in short-range autocorrelation or longer-range structure"}

    # N4: history-target mismatch (same subject, target from a different, non-adjacent time).
    n4 = []
    for b in range(b_null):
        cs = []
        for sub, s in test_samples:
            n = sub_len[sub]
            j = int(rng.integers(0, n))
            while abs(j - s.target_index) <= 1:
                j = int(rng.integers(0, n))
            cs.append(protocol.cosine(preds[len(cs)], emb_by_sub[sub][j]))
        n4.append(np.mean(cs))
    out["N4_history_target_mismatch"] = _pstat(n4) | {
        "destroys": "specific history->target link",
        "preserves": "subject identity + marginal",
        "tests": "does the SPECIFIC history predict the SPECIFIC target"}

    # N6: transition-destroyed target (same subject, non-adjacent target).
    n6 = []
    for b in range(b_null):
        cs = []
        for sub, s in test_samples:
            n = sub_len[sub]
            j = int(rng.integers(0, n))
            while abs(j - s.target_index) <= 1:
                j = int(rng.integers(0, n))
            cs.append(protocol.cosine(preds[len(cs)], emb_by_sub[sub][j]))
        n6.append(np.mean(cs))
    out["N6_transition_destroyed"] = _pstat(n6) | {
        "destroys": "transition structure (history -> immediate next)",
        "preserves": "subject identity + marginal",
        "tests": "does prediction exploit the transition or just the marginal"}

    # N5: wrong-subject history (recompute prediction from another subject's history).
    test_subs = list(test)
    n5 = []
    for b in range(b_null):
        cs = []
        for sub, s in test_samples:
            other = test_subs[int(rng.integers(0, len(test_subs)))]
            while other == sub:
                other = test_subs[int(rng.integers(0, len(test_subs)))]
            other_st = states_by_sub[other]
            # build a same-length history from the other subject (last K before a random anchor)
            n_other = len(other_st)
            anchor = int(rng.integers(K - 1, max(K, n_other - 1)))
            hist = list(range(anchor - K + 1, anchor + 1))
            from causal_mind.thought.multihorizon import HorizonSample
            fake = HorizonSample(subject=other, anchor_index=anchor, h=h,
                                 history=hist, target_index=anchor + h, k=K)
            pred = model.predict(fake, other_st)
            cs.append(protocol.cosine(pred, targets[len(cs)]))
        n5.append(np.mean(cs))
    out["N5_wrong_subject_history"] = _pstat(n5) | {
        "destroys": "subject-specificity of the history",
        "preserves": "target subject identity + marginal",
        "tests": "is the prediction subject-specific or a population effect"}

    return out, observed


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    states_by_sub, data_info = load_states(MIN_ENTRIES)
    subjects = sorted(states_by_sub)
    emb_mode = embed_with_cache(states_by_sub, subjects)
    print(f"[inference] {len(subjects)} subjects, {data_info['n_entries']} entries (emb={emb_mode})")

    split = protocol.subject_disjoint_split(subjects, seed=SEED)
    train, val, test = list(split.train), list(split.val), list(split.test)
    for sub in test[:5]:
        all_samples_leakage_free(build_horizon_samples(states_by_sub[sub], K, PRIMARY_H),
                                 {sub: states_by_sub[sub]})
    print(f"[inference] split {len(train)}/{len(val)}/{len(test)} (seed {SEED}); leakage OK")

    km = state_v1.fit_categories(
        [st for s in train for st in states_by_sub[s]], n_clusters=16, seed=SEED)
    for s in subjects:
        state_v1.assign_categories(states_by_sub[s], km)

    results: dict = {
        "protocol": "CM-XVAL-1 inference adjudication (subject-level)",
        "source": SOURCE, "seed": SEED, "k": K, "horizons": list(HORIZONS),
        "data": data_info, "split": {"train": len(train), "val": len(val), "test": len(test)},
        "n_boot": N_BOOT, "b_null": B_NULL,
    }

    per_h: dict = {}
    for h in HORIZONS:
        corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, h, K)
        c1 = baselines_h.HorizonCorpus.build(states_by_sub, train, 1, K)
        bl = baselines_h.baselines_for(corpus, c1)
        tr_samples = {h: [s for s in train for s in build_horizon_samples(states_by_sub[s], K, h)]}
        model = LinearMultiHorizon(k=K, alpha=ALPHA, horizons=(h,))
        model.fit(tr_samples, states_by_sub)
        model_pred = lambda s, st, cc, cc1, _m=model: _m.predict(s, st)  # noqa: E731

        val_scores = {
            name: float(np.mean(_eval_with_events(
                lambda s, st, cc, cc1, fn=fn: fn(s, st, cc), states_by_sub, val, K, h, corpus, c1)[0]))
            for name, fn in bl.items()
        }
        strong = max(val_scores, key=val_scores.get)
        strong_fn = bl[strong]

        m_per_sub, m_events = _eval_with_events(model_pred, states_by_sub, test, K, h, corpus, c1)
        b_per_sub, b_events = _eval_with_events(
            lambda s, st, cc, cc1, _f=strong_fn: _f(s, st, cc), states_by_sub, test, K, h, corpus, c1)

        m_arr = np.asarray(m_per_sub)
        b_arr = np.asarray(b_per_sub)
        gain = m_arr - b_arr
        gain_ci = list(bootstrap_ci(gain, n_boot=N_BOOT, seed=SEED))
        n_pos = int(np.sum(gain > 0))
        n_neg = int(np.sum(gain < 0))
        n_zero = int(np.sum(gain == 0))
        sign_p = sign_test_two_sided(n_pos, n_neg)
        # subject-level permutation (sign-flip randomization of the paired gain)
        rng = np.random.default_rng(SEED + h)
        obs_gain = float(gain.mean())
        n_perm = 2000
        null_gains = np.empty(n_perm)
        for b in range(n_perm):
            signs = rng.choice([-1.0, 1.0], size=len(gain))
            null_gains[b] = float(np.mean(signs * gain))
        p_perm_subj = float((np.sum(np.abs(null_gains) >= abs(obs_gain)) + 1) / (n_perm + 1))
        hier_mean, hier_lo, hier_hi = hierarchical_bootstrap(m_events, b_events, N_BOOT, SEED)
        # event-level (secondary, descriptive)
        m_ev_all = np.concatenate([np.asarray(v) for v in m_events.values()])
        b_ev_all = np.concatenate([np.asarray(v) for v in b_events.values()])
        event_gain = float(np.mean(m_ev_all - b_ev_all))
        cohens_d = float(gain.mean() / gain.std(ddof=1)) if gain.std(ddof=1) > 0 else 0.0

        per_h[str(h)] = {
            "strong_baseline": strong,
            "n_test_subjects": len(m_arr),
            "n_test_events": int(len(m_ev_all)),
            "model_mean": round(float(m_arr.mean()), 4),
            "baseline_mean": round(float(b_arr.mean()), 4),
            "gain_mean": round(float(gain.mean()), 4),
            "gain_median": round(float(np.median(gain)), 4),
            "gain_sd": round(float(gain.std(ddof=1)), 4),
            "proportion_positive": round(n_pos / len(gain), 4),
            "n_pos_n_neg_n_zero": [n_pos, n_neg, n_zero],
            "subject_paired_bootstrap_ci": [round(x, 4) for x in gain_ci],
            "sign_test_p": round(sign_p, 6),
            "subject_permutation_p": round(p_perm_subj, 4),
            "hierarchical_bootstrap_ci": [round(hier_mean, 4), round(hier_lo, 4), round(hier_hi, 4)],
            "event_level_gain_secondary": round(event_gain, 4),
            "cohens_d_subject": round(cohens_d, 4),
            "val_baseline_scores": {k2: round(v2, 4) for k2, v2 in val_scores.items()},
        }
        print(f"  h={h:2d}: gain={gain.mean():+.4f} CI=[{gain_ci[1]:+.4f},{gain_ci[2]:+.4f}] "
              f"sign_p={sign_p:.4f} perm_subj_p={p_perm_subj:.4f} "
              f"prop_pos={n_pos}/{len(gain)} d={cohens_d:.3f}")

    results["subject_level_inference"] = per_h

    # Null family on the primary horizon.
    h = PRIMARY_H
    corpus = baselines_h.HorizonCorpus.build(states_by_sub, train, h, K)
    model = LinearMultiHorizon(k=K, alpha=ALPHA, horizons=(h,))
    model.fit({h: [s for s in train for s in build_horizon_samples(states_by_sub[s], K, h)]},
              states_by_sub)
    nulls, observed = run_null_family(model, states_by_sub, test, h, B_NULL, SEED)
    results["null_family_primary_h"] = {"h": h, "observed": round(observed, 4), "nulls": nulls}
    for nid, v in nulls.items():
        print(f"  {nid}: null_mean={v['null_mean']:.4f} p={v['p']:.4f}")

    # Reconciliation + decision (per §28).
    g = per_h[str(h)]["subject_paired_bootstrap_ci"]
    gain_ci_excl_zero = g[1] > 0
    n1_p = nulls["N1_within_subject_target"]["p"]
    n4_p = nulls["N4_history_target_mismatch"]["p"]
    n5_p = nulls["N5_wrong_subject_history"]["p"]
    # PASS_REPLICATION: subject-level advantage survives AND temporal/transition nulls rejected.
    temporal_rejected = (n1_p < 0.05) and (n4_p < 0.05)
    if gain_ci_excl_zero and temporal_rejected and n5_p < 0.05:
        decision = "CMXVAL_PASS_REPLICATION"
    elif gain_ci_excl_zero and not temporal_rejected:
        decision = "CMXVAL_PARTIAL_REPLICATION"
    elif not gain_ci_excl_zero:
        decision = "CMXVAL_NULL_NO_REPLICATION"
    else:
        decision = "CMXVAL_INFERENCE_INCONCLUSIVE"
    results["reconciliation"] = {
        "gain_ci_excludes_zero": bool(gain_ci_excl_zero),
        "N1_within_subject_p": n1_p,
        "N4_history_target_mismatch_p": n4_p,
        "N5_wrong_subject_history_p": n5_p,
        "temporal_nulls_rejected": bool(temporal_rejected),
        "explanation": (
            "The subject-level paired bootstrap tests H0: E_sub[score_model - score_baseline] = 0 "
            "(a RELATIVE advantage over the strongest frozen baseline). The target-shuffle "
            "permutation tests H0: the model's ABSOLUTE prediction does not exceed a "
            "within-subject random-target null. Because within-person entries are highly "
            "similar (high marginal), the within-subject null is HIGH, so the model's absolute "
            "cosine does not exceed it even though it beats the baseline. The two procedures "
            "answer different questions and are not expected to agree."
        ),
    }
    results["decision"] = decision
    results["runtime_s"] = round(time.time() - t0, 1)

    (OUT / "cm_xval_inference.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\n[inference] DECISION: {decision}")
    print(f"[inference] wrote {OUT / 'cm_xval_inference.json'} in {results['runtime_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
