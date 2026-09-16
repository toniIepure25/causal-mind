"""CM-6A observational causal candidate analysis on ds006067 thought trajectories.

Runs the 7 required analyses on the real data and writes:
  * reports/cm6_observational_results.json  (per-dimension / per-subject results)
  * reports/cm6_candidate_scm.json          (machine-readable candidate SCM)

SCIENTIFIC FRAMING: this uses OBSERVATIONAL data only to generate and constrain
CANDIDATE causal hypotheses. No observational edge is a "causal discovery". The
identifiability audit (analysis 7) is expected to mark almost every edge
NOT identifiable (unmeasured confounding, no randomization). A clean negative
identification result is the correct, valuable outcome.

HARD RULES enforced here:
  * subject-disjoint splits (fit on train, evaluate on held-out test subjects);
  * no future information used as a feature (history strictly before target);
  * no held-out subject statistics leaked into features (standardize on train only).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/home/jovyan/work/causal-mind-v2")
sys.path.insert(0, str(ROOT / "src"))

from causal_mind.causal import (  # noqa: E402
    CandidateSCM,
    Edge,
    EdgeLabel,
    NodeSpec,
    NodeType,
    counterfactual_identifiability_audit,
)
from causal_mind.data.osf_a56rm import RATING_DIMS, all_subjects, load_thought_events  # noqa: E402
from causal_mind.thought.encode import MiniLMEncoder  # noqa: E402
from causal_mind.utils.splits import make_subject_disjoint_split  # noqa: E402

REPORTS = ROOT / "reports"
ALPHA = 0.05
MAX_LAG = 3

CONT_DIMS: tuple[str, ...] = RATING_DIMS + ("n_words", "duration", "gap")
DIM_INDEX = {d: i for i, d in enumerate(CONT_DIMS)}


# ---------------------------------------------------------------------------
# data loading
# ---------------------------------------------------------------------------
def _load_subject_embeddings(subjects: list[str]) -> dict[str, np.ndarray]:
    enc = MiniLMEncoder()
    out: dict[str, np.ndarray] = {}
    for s in subjects:
        evs = load_thought_events(s)
        texts = [e["transcript"] for e in evs]
        from causal_mind.thought.encode import encode_subject_cached

        out[s] = encode_subject_cached(enc, s, texts)
    return out


def _subject_matrix(subject: str, emb: np.ndarray) -> dict[str, np.ndarray]:
    evs = load_thought_events(subject)
    n = len(evs)
    X = np.zeros((n, len(CONT_DIMS)), dtype=float)
    cat = np.zeros(n, dtype=int)
    topic = np.empty(n, dtype=object)
    starts = np.array([e["onset"] for e in evs], dtype=float)
    for t, e in enumerate(evs):
        r = e["ratings"]
        for d in RATING_DIMS:
            X[t, DIM_INDEX[d]] = float(r.get(d, 0.0))
        X[t, DIM_INDEX["n_words"]] = float(len(e["transcript"].split()))
        X[t, DIM_INDEX["duration"]] = float(e["duration"])
        cat[t] = int(e["observed_category"] or 0)
        topic[t] = e["topic"]
    gap = np.zeros(n, dtype=float)
    if n > 1:
        gap[1:] = np.diff(starts)
    X[:, DIM_INDEX["gap"]] = gap
    return {"X": X, "E": np.asarray(emb, dtype=float), "cat": cat, "topic": topic}


def load_all(subjects: list[str]) -> dict[str, dict[str, np.ndarray]]:
    print("loading embeddings ...", flush=True)
    emb = _load_subject_embeddings(subjects)
    data: dict[str, dict[str, np.ndarray]] = {}
    for s in subjects:
        data[s] = _subject_matrix(s, emb[s])
    return data


# ---------------------------------------------------------------------------
# regression helpers (leakage-safe: standardize on train only)
# ---------------------------------------------------------------------------
def _standardize_fit(Xtr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0)
    sd[sd == 0] = 1.0
    return mu, sd


def _ridge_solve(Xtr: np.ndarray, ytr: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    X = np.column_stack([np.ones(len(Xtr)), Xtr])
    A = X.T @ X + alpha * np.eye(X.shape[1])
    A[0, 0] -= alpha  # do not regularize the intercept
    return np.linalg.solve(A, X.T @ ytr)


def _r2(yte: np.ndarray, yhat: np.ndarray) -> float:
    ss_res = float(((yte - yhat) ** 2).sum())
    ss_tot = float(((yte - yte.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0


def _pool_ar(data: dict, subjects: list[str], d: str, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Pool AR(k) samples for dimension d over ``subjects``: lags -> next value."""
    di = DIM_INDEX[d]
    feats: list[np.ndarray] = []
    targ: list[np.ndarray] = []
    for s in subjects:
        X = data[s]["X"]
        n = len(X)
        for t in range(k - 1, n - 1):
            feats.append(X[t - k + 1 : t + 1, di])
            targ.append(X[t + 1, di])
    return np.vstack(feats), np.vstack(targ)


def ar_skill(data: dict, train: list[str], test: list[str], d: str, k: int) -> float:
    Ftr, ytr = _pool_ar(data, train, d, k)
    Fte, yte = _pool_ar(data, test, d, k)
    if len(Ftr) < k + 2 or len(Fte) < 2:
        return float("nan")
    mu, sd = _standardize_fit(Ftr)
    Ftr_s = (Ftr - mu) / sd
    Fte_s = (Fte - mu) / sd
    coef = _ridge_solve(Ftr_s, ytr)
    yhat = Fte_s @ coef[1:] + coef[0]
    return _r2(yte, yhat)


def _pool_ar_multi(data: dict, subjects: list[str], k: int) -> tuple[np.ndarray, np.ndarray]:
    """Pool AR(k) samples for the embedding: lags (k*384) -> next embedding (384)."""
    feats: list[np.ndarray] = []
    targ: list[np.ndarray] = []
    for s in subjects:
        E = data[s]["E"]
        n = len(E)
        for t in range(k - 1, n - 1):
            feats.append(E[t - k + 1 : t + 1].reshape(-1))
            targ.append(E[t + 1])
    return np.vstack(feats), np.vstack(targ)


def semantic_skill(data: dict, train: list[str], test: list[str], k: int) -> dict:
    Ftr, ytr = _pool_ar_multi(data, train, k)
    Fte, yte = _pool_ar_multi(data, test, k)
    if len(Ftr) < k + 2 or len(Fte) < 2:
        return {"r2": float("nan"), "cosine": float("nan")}
    mu, sd = _standardize_fit(Ftr)
    Ftr_s = (Ftr - mu) / sd
    Fte_s = (Fte - mu) / sd
    coef = _ridge_solve(Ftr_s, ytr, alpha=10.0)
    yhat = Fte_s @ coef[1:] + coef[0]
    r2 = float(np.mean([_r2(yte[:, j], yhat[:, j]) for j in range(yte.shape[1])]))
    a = yte / (np.linalg.norm(yte, axis=1, keepdims=True) + 1e-9)
    b = yhat / (np.linalg.norm(yhat, axis=1, keepdims=True) + 1e-9)
    cos = float((a * b).sum(axis=1).mean())
    return {"r2": r2, "cosine": cos}


# ---------------------------------------------------------------------------
# pooled transition matrices (precomputed once, reused by analyses 2/3/6)
# ---------------------------------------------------------------------------
def pooled_transitions(data: dict, subjects: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Return (X_t, X_t1): stacked current-state and next-state rows over subjects."""
    cur: list[np.ndarray] = []
    nxt: list[np.ndarray] = []
    for s in subjects:
        X = data[s]["X"]
        n = len(X)
        if n < 2:
            continue
        cur.append(X[:-1])
        nxt.append(X[1:])
    return np.vstack(cur), np.vstack(nxt)


def _pair_arrays(
    X_t: np.ndarray, X_t1: np.ndarray, a: str, b: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ai, bi = DIM_INDEX[a], DIM_INDEX[b]
    others = [i for i in range(len(CONT_DIMS)) if i not in (ai, bi)]
    return X_t[:, ai], X_t1[:, bi], X_t[:, others]


# ---------------------------------------------------------------------------
# analysis 2: conditional-independence structure
# ---------------------------------------------------------------------------
def ci_structure(X_t: np.ndarray, X_t1: np.ndarray) -> list[dict]:
    from causal_mind.causal import fisher_z_test

    out: list[dict] = []
    for a in CONT_DIMS:
        for b in CONT_DIMS:
            if a == b:
                continue
            x, y, z = _pair_arrays(X_t, X_t1, a, b)
            res = fisher_z_test(x, y, z)
            out.append(
                {
                    "src": a,
                    "dst": b,
                    "p": float(res["p"]),
                    "r_partial": float(res["r_partial"]),
                    "n": int(res["n"]),
                    "conditionally_dependent": bool(res["p"] < ALPHA),
                }
            )
    return out


# ---------------------------------------------------------------------------
# analysis 3: incremental value (partial information)
# ---------------------------------------------------------------------------
def incremental_value(
    Xtr_t: np.ndarray, Xtr_t1: np.ndarray, Xte_t: np.ndarray, Xte_t1: np.ndarray, a: str, b: str
) -> float:
    """Incremental R^2 of adding antecedent a to predict b[t+1] given the others."""
    xtr, ytr, ztr = _pair_arrays(Xtr_t, Xtr_t1, a, b)
    xte, yte, zte = _pair_arrays(Xte_t, Xte_t1, a, b)
    if len(xtr) < 20 or len(xte) < 5:
        return float("nan")

    def r2_with(use_a: bool) -> float:
        Ftr = np.column_stack([ztr, xtr]) if use_a else ztr
        Fte = np.column_stack([zte, xte]) if use_a else zte
        mu, sd = _standardize_fit(Ftr)
        Ftr_s = (Ftr - mu) / sd
        Fte_s = (Fte - mu) / sd
        coef = _ridge_solve(Ftr_s, ytr)
        yhat = Fte_s @ coef[1:] + coef[0]
        return _r2(yte, yhat)

    return r2_with(True) - r2_with(False)


# ---------------------------------------------------------------------------
# analysis 4: transition asymmetries
# ---------------------------------------------------------------------------
def _transition_matrix(seq: np.ndarray, values: list) -> np.ndarray:
    idx = {v: i for i, v in enumerate(values)}
    m = np.zeros((len(values), len(values)))
    for t in range(len(seq) - 1):
        i, j = seq[t], seq[t + 1]
        if i in idx and j in idx:
            m[idx[i], idx[j]] += 1
    row = m.sum(axis=1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(row > 0, m / np.where(row > 0, row, 1), 0.0)
    return p


def transition_asymmetries(data: dict, subjects: list[str]) -> dict:
    cat_vals = [1, 2, 3, 4, 5, 6]
    cat_seq = np.concatenate([data[s]["cat"] for s in subjects])
    cat_p = _transition_matrix(cat_seq, cat_vals)
    cat_asym = []
    for i in range(len(cat_vals)):
        for j in range(i + 1, len(cat_vals)):
            cat_asym.append(
                {
                    "i": cat_vals[i],
                    "j": cat_vals[j],
                    "p_ij": float(cat_p[i, j]),
                    "p_ji": float(cat_p[j, i]),
                    "asym": float(cat_p[i, j] - cat_p[j, i]),
                }
            )

    # topic self-persistence
    topic_same = 0
    topic_total = 0
    for s in subjects:
        tp = data[s]["topic"]
        for t in range(len(tp) - 1):
            topic_total += 1
            if tp[t] == tp[t + 1]:
                topic_same += 1
    topic_persist = topic_same / topic_total if topic_total else 0.0

    # affect (emotional_intensity) binarized transition
    ei = np.concatenate([data[s]["X"][:, DIM_INDEX["emotional_intensity"]] for s in subjects])
    med = float(np.median(ei))
    binseq = (ei > med).astype(int)
    aff_p = _transition_matrix(binseq, [0, 1])
    aff_asym = float(aff_p[0, 1] - aff_p[1, 0])

    return {
        "category_transition": {
            "values": cat_vals,
            "matrix": cat_p.tolist(),
            "asymmetries": cat_asym,
        },
        "topic_self_persistence": float(topic_persist),
        "affect_transition": {
            "threshold": med,
            "matrix": aff_p.tolist(),
            "asym_high_to_low_minus_low_to_high": aff_asym,
        },
    }


# ---------------------------------------------------------------------------
# analysis 5: stability across subjects
# ---------------------------------------------------------------------------
def per_subject_ar1(data: dict, subjects: list[str], d: str) -> list[float]:
    di = DIM_INDEX[d]
    out: list[float] = []
    for s in subjects:
        X = data[s]["X"][:, di]
        n = len(X)
        if n < 6:
            out.append(float("nan"))
            continue
        x = X[:-1]
        y = X[1:]
        mu, sd = _standardize_fit(x.reshape(-1, 1))
        xs = (x - mu[0]) / sd[0]
        coef = _ridge_solve(xs.reshape(-1, 1), y)
        yhat = xs * coef[1] + coef[0]
        out.append(_r2(y, yhat))
    return out


def stability(data: dict, subjects: list[str]) -> dict:
    per_dim: dict[str, dict] = {}
    for d in CONT_DIMS:
        vals = [v for v in per_subject_ar1(data, subjects, d) if not np.isnan(v)]
        vals = np.array(vals)
        per_dim[d] = {
            "mean": float(vals.mean()),
            "std": float(vals.std()),
            "min": float(vals.min()),
            "max": float(vals.max()),
            "frac_positive": float((vals > 0).mean()),
            "n_subjects": int(len(vals)),
        }
    return {"per_dimension_ar1": per_dim}


# ---------------------------------------------------------------------------
# analysis 6: candidate mediator / moderator
# ---------------------------------------------------------------------------
def mediator_moderator(X_t: np.ndarray, X_t1: np.ndarray) -> list[dict]:
    from causal_mind.causal import fisher_z_test

    targets = ["emotional_intensity", "joy", "anxiety"]
    antecedents = [
        "vision", "audition", "interoception", "somatosensation", "n_words", "duration", "gap"
    ]
    out: list[dict] = []
    for b in targets:
        for a in antecedents:
            for m in antecedents:
                if m == a:
                    continue
                # (i) a[t] ~ m[t]; (ii) m[t] ~ b[t+1] | a[t]; (iii) a[t] ~ b[t+1]
                xam, yam, _ = _pair_arrays(X_t, X_t1, a, m)
                p_am = fisher_z_test(xam, yam)["p"]
                xmb, ymb, zmb = _pair_arrays(X_t, X_t1, m, b)
                p_mb_given_a = fisher_z_test(xmb, ymb, zmb)["p"]
                xab, yab, _ = _pair_arrays(X_t, X_t1, a, b)
                p_ab = fisher_z_test(xab, yab)["p"]
                is_mediator = bool(p_am < ALPHA and p_mb_given_a < ALPHA and p_ab < ALPHA)
                out.append(
                    {
                        "antecedent": a,
                        "mediator": m,
                        "target": b,
                        "p_a_m": float(p_am),
                        "p_m_b_given_a": float(p_mb_given_a),
                        "p_a_b": float(p_ab),
                        "candidate_mediator": is_mediator,
                    }
                )
    return out


# ---------------------------------------------------------------------------
# analysis 7: counterfactual identifiability audit (per candidate edge)
# ---------------------------------------------------------------------------
def _audit_edge(a: str, b: str) -> dict:
    import networkx as nx

    G = nx.DiGraph()
    G.add_nodes_from([f"{a}_t", f"{b}_t1", "latent_U_t"])
    G.add_edges_from([(f"{a}_t", f"{b}_t1"), ("latent_U_t", f"{a}_t"), ("latent_U_t", f"{b}_t1")])
    observed = {f"{a}_t", f"{b}_t1"}
    return counterfactual_identifiability_audit(
        G, f"{a}_t", f"{b}_t1", observed,
        assumptions=["ignorability given latent_U_t (UNMET: latent_U_t unmeasured)"],
    )


# ---------------------------------------------------------------------------
# label assignment
# ---------------------------------------------------------------------------
def assign_label(audit: dict, conditional: bool, marginal: bool, temporal: bool) -> EdgeLabel:
    identifiable = audit["status"] == "identifiable"
    if identifiable and conditional:
        return EdgeLabel.CAUSALLY_IDENTIFIED
    if conditional:
        return EdgeLabel.CONDITIONALLY_SUPPORTED
    if identifiable:
        return EdgeLabel.TEMPORALLY_PRECEDENT
    if temporal and marginal:
        return EdgeLabel.TEMPORALLY_PRECEDENT
    if marginal:
        return EdgeLabel.ASSOCIATIONAL
    return EdgeLabel.NOT_IDENTIFIABLE


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main() -> None:
    t0 = time.time()
    subjects = all_subjects()
    print(f"n_subjects={len(subjects)}", flush=True)
    data = load_all(subjects)

    split = make_subject_disjoint_split(subjects, train_frac=0.6, val_frac=0.2, seed=0)
    train = list(split.train)
    test = list(split.test)
    print(f"train={len(train)} val={len(split.val)} test={len(test)}", flush=True)

    Xtr_t, Xtr_t1 = pooled_transitions(data, train)
    Xte_t, Xte_t1 = pooled_transitions(data, test)

    results: dict = {
        "meta": {
            "n_subjects": len(subjects),
            "split": {"train": train, "val": list(split.val), "test": test, "seed": split.seed},
            "alpha": ALPHA,
            "max_lag": MAX_LAG,
            "cont_dims": list(CONT_DIMS),
            "note": (
                "OBSERVATIONAL candidate analysis. No edge is a causal discovery. "
                "Identifiability audit (analysis 7) is expected to mark almost all "
                "edges not identifiable (unmeasured confounding, no randomization)."
            ),
        }
    }

    # ---- analysis 1: lagged predictive relationships ----
    print("analysis 1: lagged skill ...", flush=True)
    a1: dict[str, dict] = {}
    for d in CONT_DIMS:
        a1[d] = {str(k): ar_skill(data, train, test, d, k) for k in range(1, MAX_LAG + 1)}
    a1["semantic_state"] = {
        str(k): semantic_skill(data, train, test, k) for k in range(1, MAX_LAG + 1)
    }
    results["analysis_1_lagged_skill"] = a1

    # ---- analysis 2: CI structure (train subjects, descriptive) ----
    print("analysis 2: CI structure ...", flush=True)
    a2 = ci_structure(Xtr_t, Xtr_t1)
    results["analysis_2_ci_structure"] = a2

    # ---- analysis 3: incremental value (fit train, eval test) ----
    print("analysis 3: incremental value ...", flush=True)
    a3: list[dict] = []
    for a in CONT_DIMS:
        for b in CONT_DIMS:
            if a == b:
                continue
            inc = incremental_value(Xtr_t, Xtr_t1, Xte_t, Xte_t1, a, b)
            a3.append({"src": a, "dst": b, "incremental_r2": float(inc)})
    results["analysis_3_incremental_value"] = a3

    # ---- analysis 4: transition asymmetries ----
    print("analysis 4: transitions ...", flush=True)
    results["analysis_4_transitions"] = transition_asymmetries(data, subjects)

    # ---- analysis 5: stability ----
    print("analysis 5: stability ...", flush=True)
    results["analysis_5_stability"] = stability(data, subjects)

    # ---- analysis 6: mediator / moderator (train subjects, descriptive) ----
    print("analysis 6: mediator/moderator ...", flush=True)
    results["analysis_6_mediator_moderator"] = mediator_moderator(Xtr_t, Xtr_t1)

    # ---- analysis 7: identifiability audit (per candidate edge) ----
    print("analysis 7: identifiability audit ...", flush=True)
    # candidate edges = conditionally dependent pairs (analysis 2) + AR edges
    cond_pairs = {(r["src"], r["dst"]) for r in a2 if r["conditionally_dependent"]}
    ar_pairs = {(d, d) for d in CONT_DIMS}
    candidate_edges = sorted(cond_pairs | ar_pairs)
    a7: list[dict] = []
    for a, b in candidate_edges:
        audit = _audit_edge(a, b)
        a7.append({"src": a, "dst": b, **audit})
    n_ident = sum(1 for r in a7 if r["status"] == "identifiable")
    results["analysis_7_identifiability"] = {
        "n_candidate_edges": len(a7),
        "n_identifiable": n_ident,
        "n_not_identifiable": len(a7) - n_ident,
        "edges": a7,
    }

    # ---- candidate SCM ----
    print("building candidate SCM ...", flush=True)
    scm = _build_scm(a1, a2, a3, a7, candidate_edges)
    REPORTS.mkdir(parents=True, exist_ok=True)
    scm.to_json(REPORTS / "cm6_candidate_scm.json")

    # ---- summary / ranking ----
    results["candidate_ranking"] = _rank_candidates(a1, a3, results["analysis_5_stability"], a2)
    results["label_counts"] = scm.label_counts()

    out = REPORTS / "cm6_observational_results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"WROTE {out}", flush=True)
    print(f"WROTE {REPORTS / 'cm6_candidate_scm.json'}", flush=True)
    print(f"DONE in {time.time() - t0:.0f}s", flush=True)


AR_CONDITIONAL_SKILL = 0.05  # lag-1 R^2 threshold for an AR edge to count as conditionally supported


def _build_scm(
    a1: dict, a2: list[dict], a3: list[dict], a7: list[dict], candidate_edges: list[tuple[str, str]]
) -> CandidateSCM:
    audit_by_edge = {(r["src"], r["dst"]): r for r in a7}
    inc_by_edge = {(r["src"], r["dst"]): r["incremental_r2"] for r in a3}
    ci_by_edge = {(r["src"], r["dst"]): r for r in a2}

    scm = CandidateSCM(
        name="cm6_candidate_dynamic_cognitive_scm",
        structural_equation="Z[t+1] = f(Z[t], Z[t-1:t-k], context[t], latent_U[t])",
        assumptions=[
            "temporal precedence: antecedents at t, outcomes at t+1",
            "ignorability given latent_U[t] (UNMET: latent_U[t] unmeasured)",
            "no unmeasured confounding (UNMET: latent_U[t] is a common cause)",
            "stationarity of the transition within a scan",
        ],
    )
    # nodes
    affect_dims = set(RATING_DIMS[:8])
    sensory_dims = set(RATING_DIMS[8:])
    for d in CONT_DIMS:
        if d in affect_dims:
            nt = NodeType.AFFECT
        elif d in sensory_dims:
            nt = NodeType.SENSORY_MODAL
        elif d in ("n_words", "duration"):
            nt = NodeType.LINGUISTIC
        else:
            nt = NodeType.TEMPORAL
        scm.nodes[f"{d}_t"] = NodeSpec(f"{d}_t", nt, f"{d} at time t", observed=True)
        scm.nodes[f"{d}_t1"] = NodeSpec(f"{d}_t1", nt, f"{d} at time t+1", observed=True)
    scm.nodes["semantic_state_t"] = NodeSpec(
        "semantic_state_t", NodeType.SEMANTIC_STATE, "embedding at t", observed=True
    )
    scm.nodes["semantic_state_t1"] = NodeSpec(
        "semantic_state_t1", NodeType.SEMANTIC_STATE, "embedding at t+1", observed=True
    )
    scm.nodes["category_t"] = NodeSpec(
        "category_t", NodeType.CATEGORY, "observed category at t", observed=True
    )
    scm.nodes["category_t1"] = NodeSpec(
        "category_t1", NodeType.CATEGORY, "observed category at t+1", observed=True
    )
    scm.nodes["topic_t"] = NodeSpec("topic_t", NodeType.TOPIC, "topic at t", observed=True)
    scm.nodes["topic_t1"] = NodeSpec("topic_t1", NodeType.TOPIC, "topic at t+1", observed=True)
    scm.nodes["latent_U_t"] = NodeSpec(
        "latent_U_t", NodeType.LATENT_U, "unmeasured confounder at t", observed=False
    )

    # confounding edges (latent_U_t -> every state node)
    confound_just = "unmeasured common cause (latent confounding)"
    for name in list(scm.nodes):
        if name == "latent_U_t":
            continue
        scm.edges.append(Edge("latent_U_t", name, EdgeLabel.ASSOCIATIONAL, confound_just))

    # AR + cross candidate edges
    for a, b in candidate_edges:
        audit = audit_by_edge.get((a, b))
        if audit is None:
            audit = _audit_edge(a, b)
        if a == b:
            # AR edge: observational support is the lag-1 autoregressive skill.
            skill = a1.get(a, {}).get("1", float("nan"))
            skill = float(skill) if isinstance(skill, (int, float)) else float("nan")
            marginal = bool(not np.isnan(skill) and skill > 0)
            conditional = bool(not np.isnan(skill) and skill > AR_CONDITIONAL_SKILL)
            inc = float("nan")
            ci = None
            mp = float("nan")
            just = (
                f"AR edge; audit={audit['status']}; lag1_skill_r2={skill:.3f}; "
                f"conditional={conditional}. {audit['reason']}"
            )
        else:
            ci = ci_by_edge.get((a, b))
            inc = inc_by_edge.get((a, b), float("nan"))
            conditional = bool(ci is not None and ci["conditionally_dependent"] and inc > 0)
            marginal = bool(ci is not None and ci["p"] < ALPHA)
            mp = ci["p"] if ci else float("nan")
            just = (
                f"audit={audit['status']}; conditional={conditional}; "
                f"marginal_p={mp:.3g}; incr_r2={inc:.3f}. {audit['reason']}"
            )
        temporal = True  # a at t, b at t+1 by construction
        label = assign_label(audit, conditional, marginal, temporal)
        meta = {
            "identifiable": audit["status"] == "identifiable",
            "audit_status": audit["status"],
            "audit_reason": audit["reason"],
            "adjustment_set": audit["adjustment_set"],
            "incremental_r2": float(inc) if not np.isnan(inc) else None,
            "ci_p": float(ci["p"]) if ci else None,
            "ci_r_partial": float(ci["r_partial"]) if ci else None,
            "lag1_skill_r2": (
                float(a1.get(a, {}).get("1", float("nan")))
                if a == b and isinstance(a1.get(a, {}).get("1"), (int, float))
                else None
            ),
        }
        scm.edges.append(Edge(f"{a}_t", f"{b}_t1", label, just, metadata=meta))
    return scm


def _rank_candidates(a1: dict, a3: list[dict], a5: dict, a2: list[dict]) -> list[dict]:
    """Rank antecedent dimensions by observational support (lagged skill +
    incremental value + cross-subject stability)."""
    inc_by_src: dict[str, list[float]] = {}
    for r in a3:
        inc_by_src.setdefault(r["src"], []).append(r["incremental_r2"])
    cond_by_src: dict[str, int] = {}
    for r in a2:
        if r["conditionally_dependent"]:
            cond_by_src[r["src"]] = cond_by_src.get(r["src"], 0) + 1
    rows: list[dict] = []
    for d in CONT_DIMS:
        skills = [v for v in a1[d].values() if isinstance(v, float) and not np.isnan(v)]
        lag1 = a1[d].get("1", float("nan"))
        incs = [v for v in inc_by_src.get(d, []) if not np.isnan(v)]
        stab = a5["per_dimension_ar1"].get(d, {})
        rows.append(
            {
                "dimension": d,
                "lag1_skill_r2": float(lag1) if not np.isnan(lag1) else None,
                "best_lag_skill_r2": float(max(skills)) if skills else None,
                "mean_incremental_r2": float(np.mean(incs)) if incs else None,
                "n_conditionally_dependent_out": cond_by_src.get(d, 0),
                "stability_frac_positive": stab.get("frac_positive"),
                "stability_mean_ar1": stab.get("mean"),
            }
        )
    # composite score (higher = more observational support)
    for r in rows:
        s = 0.0
        s += (r["best_lag_skill_r2"] or 0.0)
        s += max(r["mean_incremental_r2"] or 0.0, 0.0) * 5.0
        s += (r["stability_frac_positive"] or 0.0) * 0.5
        s += (r["n_conditionally_dependent_out"] or 0) * 0.01
        r["support_score"] = float(s)
    rows.sort(key=lambda r: r["support_score"], reverse=True)
    return rows


if __name__ == "__main__":
    main()
