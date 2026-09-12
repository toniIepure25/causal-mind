"""Run the full CM-2 non-neural evaluation once enough transcripts are fetched.

One command, resumable, token-expiry-safe (embeddings cached to disk). Aborts
cleanly (exit 2) if fewer than MIN_SUBJECTS transcripts are present (S3 still
down), so it can be re-run after the fetch completes.

Pipeline:
  1. load all fetched subjects + embed (MiniLM, cached) + fit categories (train)
  2. subject-disjoint split + SEAL (before any test metric)
  3. train corpus
  4. baselines B0-B7 on test
  5. main model (linear transition) with VAL-based selection, final eval on test
  6. the six CM-2F analyses
  7. write results JSON + markdown report
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from causal_mind.data import osf_a56rm
from causal_mind.eval import analyses, protocol
from causal_mind.forecast import baselines, models
from causal_mind.thought import encode, prospective, state_v1

OUT = Path("/home/jovyan/work/causal-mind-v2/reports")
N_CLUSTERS = 16
SEED = 20260911
MIN_SUBJECTS = 100


def main() -> int:
    t0 = time.time()
    subs = osf_a56rm.all_subjects()
    print(f"[cm2] subjects with derived thought events: {len(subs)}")
    if len(subs) < MIN_SUBJECTS:
        print(f"[cm2] NOT ENOUGH DATA ({len(subs)} < {MIN_SUBJECTS}); "
              f"run data/scripts/build_thought_events.py after the OSF fetch.")
        return 2

    # 1. load + embed + categories
    print("[cm2] embedding (MiniLM, cached)...")
    enc = encode.MiniLMEncoder()
    states_by_sub: dict[str, list] = {}
    for s in subs:
        st = state_v1.states_from_events(s, osf_a56rm.load_thought_events(s))
        state_v1.embed_states(st, enc)
        states_by_sub[s] = st
    n_thoughts = sum(len(v) for v in states_by_sub.values())
    print(f"[cm2] {len(subs)} subjects, {n_thoughts} thoughts embedded")

    # 2. split + seal (BEFORE any test metric)
    split = protocol.subject_disjoint_split(subs, seed=SEED)
    seal = protocol.seal_split(split, seed=SEED, n_subjects=len(subs))
    print(f"[cm2] split train/val/test = "
          f"{len(split.train)}/{len(split.val)}/{len(split.test)}; seal={seal[:16]}...")

    # categories: fit on TRAIN only
    train_states = [st for s in split.train for st in states_by_sub[s]]
    km = state_v1.fit_categories(train_states, n_clusters=N_CLUSTERS, seed=SEED)
    for s in subs:
        state_v1.assign_categories(states_by_sub[s], km)

    # 3. train corpus
    corpus = baselines.TrainCorpus.build(train_states, n_clusters=N_CLUSTERS)
    test_subjects = list(split.test)
    val_subjects = list(split.val)

    results: dict = {
        "n_subjects": len(subs), "n_thoughts": n_thoughts,
        "split": {"train": len(split.train), "val": len(split.val), "test": len(split.test)},
        "seal": seal, "n_clusters": N_CLUSTERS, "seed": SEED,
        "encoder": enc.name,
    }

    # 4. baselines on test (k=1 primary)
    print("[cm2] evaluating baselines on test...")
    base_res = {}
    for name, fn in baselines.BASELINES.items():
        sc = analyses.eval_predictor(fn, states_by_sub, test_subjects, 1, corpus)
        base_res[name] = {"semantic_ci": list(analyses._mean_ci(sc.semantic, SEED)),
                          "category_ci": list(analyses._mean_ci(sc.categorical, SEED))}
        print(f"  {name:26s} sem={base_res[name]['semantic_ci'][0]:.4f}")
    results["baselines"] = base_res

    # 5. main model: linear transition, VAL-based selection over (k, alpha)
    print("[cm2] selecting main model on val...")
    def fit_lt(k: int, alpha: float):
        Xk, Yk = models.build_xy(
            prospective.build_prospective_samples(train_states, k=k), states_by_sub)
        return analyses.model_as_predictor(models.LinearTransition(k=k, alpha=alpha).fit(Xk, Yk))

    best = None
    for k in (1, 2, 3, 5):
        for alpha in (1.0, 10.0, 100.0, 1000.0):
            sc = analyses.eval_predictor(fit_lt(k, alpha), states_by_sub, val_subjects, k, corpus)
            val_score = float(np.mean(sc.semantic)) if sc.semantic else -1
            if best is None or val_score > best[0]:
                best = (val_score, k, alpha)
    val_score, best_k, best_alpha = best
    print(f"[cm2] selected k={best_k} alpha={best_alpha} (val sem={val_score:.4f})")
    main_pred = fit_lt(best_k, best_alpha)
    main_sc = analyses.eval_predictor(main_pred, states_by_sub, test_subjects, best_k, corpus)
    results["main_model"] = {
        "arch": "linear_transition", "k": best_k, "alpha": best_alpha,
        "val_sem": val_score,
        "test_sem_ci": list(analyses._mean_ci(main_sc.semantic, SEED)),
    }

    # 6. the six analyses
    print("[cm2] running the six analyses...")
    results["A1_immediate"] = analyses.immediate_predictability(
        baselines.b0_marginal, baselines.b1_previous_state,
        states_by_sub, test_subjects, 1, corpus, SEED)
    results["A2_added_history"] = analyses.added_history(
        fit_lt, states_by_sub, test_subjects, corpus, ks=(1, best_k), seed=SEED)
    results["A3_semantic_vs_categorical"] = analyses.semantic_vs_categorical(
        main_pred, states_by_sub, test_subjects, best_k, corpus, SEED)
    results["A4_cross_subject"] = analyses.cross_subject(
        main_pred, states_by_sub, test_subjects, best_k, corpus, SEED)
    results["A5_history_depth"] = analyses.history_depth_curve(
        fit_lt, states_by_sub, test_subjects, corpus, ks=(1, 2, 3, 5, 8), seed=SEED)
    results["A6_permutation_null"] = analyses.permutation_null(
        main_pred, states_by_sub, test_subjects, best_k, corpus, n_null=200, seed=SEED)

    # 7. persist
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cm2_results.json").write_text(json.dumps(results, indent=2, default=float))
    print(f"[cm2] wrote {OUT/'cm2_results.json'} in {time.time()-t0:.0f}s")
    _write_report(results)
    return 0


def _write_report(r: dict) -> None:
    def ci(x):
        return f"{x[0]:.4f} [{x[1]:.4f}, {x[2]:.4f}]"
    lines = ["# CM-2 — THOUGHT STATE + NEXT (auto-generated results)", ""]
    lines.append(f"subjects={r['n_subjects']} thoughts={r['n_thoughts']} "
                 f"split={r['split']} seal={r['seal'][:16]}... encoder={r['encoder']}")
    lines.append("\n## Baselines (test, k=1)")
    for name, v in r["baselines"].items():
        lines.append(f"- {name}: semantic {ci(v['semantic_ci'])}, category {ci(v['category_ci'])}")
    m = r["main_model"]
    lines.append(f"\n## Main model: {m['arch']} k={m['k']} alpha={m['alpha']} "
                 f"(val {m['val_sem']:.4f})")
    lines.append(f"- test semantic: {ci(m['test_sem_ci'])}")
    lines.append("\n## Analyses")
    lines.append(f"- A1 immediate: B0 {ci(r['A1_immediate']['B0_marginal'])} vs "
                 f"B1 {ci(r['A1_immediate']['B1_previous_state'])} "
                 f"(delta {ci(r['A1_immediate']['delta'])})")
    lines.append(f"- A2 added history: {r['A2_added_history']}")
    lines.append(f"- A3 semantic vs categorical: {r['A3_semantic_vs_categorical']}")
    a4 = r["A4_cross_subject"]
    lines.append(f"- A4 cross-subject: n={a4['n_test_subjects']} mean_ci={ci(a4['mean_ci'])}")
    lines.append(f"- A5 history depth: {r['A5_history_depth']}")
    a6 = r["A6_permutation_null"]
    lines.append(f"- A6 permutation null: observed={a6['observed']:.4f} "
                 f"null_mean={a6['null_mean']:.4f} p={a6['p_value']:.4f}")
    (OUT / "cm2_results.md").write_text("\n".join(lines) + "\n")
    print(f"[cm2] wrote {OUT/'cm2_results.md'}")


if __name__ == "__main__":
    raise SystemExit(main())
