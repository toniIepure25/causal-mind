"""Identifiability machinery: d-separation, conditional-independence tests,
and a backdoor-criterion audit for counterfactual / interventional estimands.

networkx >= 3.x removed ``networkx.causal_inference``, so d-separation and the
backdoor criterion are implemented here from first principles (Bayes-Ball
algorithm + Pearl's backdoor criterion). The audit is deliberately conservative:
it only reports an effect as identifiable when a *measured* adjustment set blocks
every backdoor path, and it names the unobserved nodes that prevent identification.
"""
from __future__ import annotations

import itertools
from typing import Any

import networkx as nx
import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# d-separation (Bayes-Ball)
# ---------------------------------------------------------------------------
def _collider_active(G: nx.DiGraph, n: str, Z: set[str]) -> bool:
    """A collider at ``n`` is active (path not blocked) iff n or a descendant of n is in Z."""
    if n in Z:
        return True
    return bool(set(nx.descendants(G, n)) & Z)


def d_connected(G: nx.DiGraph, x: str, y: str, Z: set[str] | None = None) -> bool:
    """True iff x and y are d-connected (some path active) given ``Z``.

    Implements the Bayes-Ball algorithm. Ball state is ``(node, dir)`` where
    ``dir == 'f'`` means the ball arrived at ``node`` travelling with the arrow
    (from a parent) and ``dir == 'b'`` means against the arrow (from a child).
    """
    if x == y:
        return True
    if x not in G or y not in G:
        return False
    Z = set(Z or set())

    from collections import deque

    seen: set[tuple[str, str]] = set()
    queue: deque[tuple[str, str]] = deque()
    # seed from x: move to children (arrive 'f') and parents (arrive 'b'); no Z check at x.
    for c in G.successors(x):
        queue.append((c, "f"))
    for p in G.predecessors(x):
        queue.append((p, "b"))

    while queue:
        node, arr = queue.popleft()
        if node == y:
            return True
        if (node, arr) in seen:
            continue
        seen.add((node, arr))
        # leave node toward a child: node is a non-collider -> blocked iff node in Z.
        if node not in Z:
            for c in G.successors(node):
                if (c, "f") not in seen:
                    queue.append((c, "f"))
        # leave node toward a parent:
        if arr == "f":
            # prev -> node <- parent : node is a COLLIDER -> active iff collider_active.
            if _collider_active(G, node, Z):
                for p in G.predecessors(node):
                    if (p, "b") not in seen:
                        queue.append((p, "b"))
        else:
            # prev <- node <- parent is impossible; prev <- node -> ... wait:
            # arrived 'b' means node -> prev. Leaving to a parent (parent -> node):
            # prev <- node <- parent? no: node->prev and parent->node => non-collider.
            if node not in Z:
                for p in G.predecessors(node):
                    if (p, "b") not in seen:
                        queue.append((p, "b"))
    return False


def d_separated(G: nx.DiGraph, x: str, y: str, Z: set[str] | None = None) -> bool:
    """True iff x and y are d-separated given ``Z``."""
    return not d_connected(G, x, y, Z)


# ---------------------------------------------------------------------------
# conditional-independence tests
# ---------------------------------------------------------------------------
def fisher_z_test(x: np.ndarray, y: np.ndarray, z: np.ndarray | None = None) -> dict[str, float]:
    """Partial-correlation (Fisher-z) CI test for continuous variables.

    ``z`` is an optional (n,) or (n, k) array of continuous conditioning variables.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    if z is None:
        Z = np.ones((n, 1))
    else:
        z = np.atleast_2d(np.asarray(z, dtype=float))
        if z.shape[0] == 1 and n != 1:
            z = z.T
        Z = np.column_stack([np.ones(n), z])
    bx, *_ = np.linalg.lstsq(Z, x, rcond=None)
    by, *_ = np.linalg.lstsq(Z, y, rcond=None)
    rx = x - Z @ bx
    ry = y - Z @ by
    denom = np.linalg.norm(rx) * np.linalg.norm(ry)
    r = float(np.dot(rx, ry) / denom) if denom > 0 else 0.0
    r = float(np.clip(r, -1.0 + 1e-12, 1.0 - 1e-12))
    fz = 0.5 * np.log((1.0 + r) / (1.0 - r))
    k = Z.shape[1] - 1  # number of conditioning variables
    dof = max(n - k - 3, 1)
    se = 1.0 / np.sqrt(dof)
    stat = float(fz / se)
    p = float(2.0 * (1.0 - stats.norm.cdf(abs(stat))))
    return {"stat": stat, "p": p, "r_partial": r, "n": n}


def _pearson_chi2(table: np.ndarray) -> tuple[float, int]:
    row = table.sum(axis=1, keepdims=True)
    col = table.sum(axis=0, keepdims=True)
    tot = float(row.sum())
    exp = row * col / tot if tot > 0 else np.zeros_like(table)
    with np.errstate(divide="ignore", invalid="ignore"):
        contrib = np.where(exp > 0, (table - exp) ** 2 / np.where(exp > 0, exp, 1.0), 0.0)
    chi2 = float(contrib.sum())
    dof = int(max((table.shape[0] - 1) * (table.shape[1] - 1), 0))
    return chi2, dof


def chi_square_ci(a: np.ndarray, b: np.ndarray, z: np.ndarray | None = None) -> dict[str, float]:
    """Stratified Pearson chi-square CI test for discrete variables.

    ``z`` is an optional discrete conditioning variable; the test sums the
    stratum-specific chi-square statistics (and degrees of freedom).
    """
    a = np.asarray(a)
    b = np.asarray(b)
    if z is None:
        z = np.zeros(len(a), dtype=int)
    z = np.asarray(z)
    stat = 0.0
    dof = 0
    for val in np.unique(z):
        m = z == val
        aa, bb = a[m], b[m]
        ca, cb = np.unique(aa), np.unique(bb)
        if len(ca) < 2 or len(cb) < 2:
            continue
        table = np.zeros((len(ca), len(cb)))
        for i, av in enumerate(ca):
            for j, bv in enumerate(cb):
                table[i, j] = float(np.sum((aa == av) & (bb == bv)))
        c, d = _pearson_chi2(table)
        stat += c
        dof += d
    p = float(stats.chi2.sf(stat, dof)) if dof > 0 else 1.0
    return {"stat": stat, "p": p, "dof": dof}


def _bin(x: np.ndarray, n_bins: int) -> np.ndarray:
    qs = np.quantile(x, np.linspace(0.0, 1.0, n_bins + 1)[1:-1])
    return np.digitize(x, qs)


def _mi_discrete(x: np.ndarray, y: np.ndarray) -> float:
    ux, uy = np.unique(x), np.unique(y)
    n = len(x)
    if n < 2 or len(ux) < 2 or len(uy) < 2:
        return 0.0
    px = np.array([(x == v).sum() for v in ux], dtype=float) / n
    py = np.array([(y == v).sum() for v in uy], dtype=float) / n
    pxy = np.array(
        [float(np.sum((x == i) & (y == j))) for i in ux for j in uy], dtype=float
    ).reshape(len(ux), len(uy)) / n
    mi = 0.0
    for i in range(len(ux)):
        for j in range(len(uy)):
            if pxy[i, j] > 0:
                mi += pxy[i, j] * np.log(pxy[i, j] / (px[i] * py[j]))
    return float(mi)


def mutual_information_ci(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray | None = None,
    n_perm: int = 200,
    seed: int = 0,
    n_bins: int = 8,
) -> dict[str, float]:
    """Conditional mutual information with a within-stratum permutation null.

    Continuous inputs are quantile-binned. The null permutes ``y`` within each
    stratum of ``z``, so the test is of *conditional* independence.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    if np.issubdtype(np.asarray(x).dtype, np.floating):
        x = _bin(x, n_bins)
    if np.issubdtype(np.asarray(y).dtype, np.floating):
        y = _bin(y, n_bins)
    if z is None:
        z = np.zeros(len(x), dtype=int)
    z = np.asarray(z)
    rng = np.random.default_rng(seed)

    def cond_mi(xx: np.ndarray, yy: np.ndarray) -> float:
        tot = 0.0
        wsum = 0.0
        for val in np.unique(z):
            m = z == val
            if m.sum() < 2:
                continue
            tot += _mi_discrete(xx[m], yy[m]) * m.sum()
            wsum += int(m.sum())
        return tot / max(wsum, 1)

    observed = cond_mi(x, y)
    nulls = []
    for _ in range(n_perm):
        yp = y.copy()
        for val in np.unique(z):
            m = z == val
            yp[m] = rng.permutation(y[m])
        nulls.append(cond_mi(x, yp))
    nulls = np.asarray(nulls)
    p = float((np.sum(nulls >= observed) + 1) / (n_perm + 1))
    return {"stat": observed, "p": p, "null_mean": float(nulls.mean())}


def ci_test(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray | None = None,
    method: str = "auto",
    **kw: Any,
) -> dict[str, float]:
    """Dispatch a conditional-independence test.

    ``method`` in {"fisher_z", "chi2", "mi", "auto"}. "auto" picks fisher_z when
    both margins look continuous, chi2 when both look discrete, else mi.
    """
    xa, ya = np.asarray(x), np.asarray(y)
    if method == "auto":
        xc = np.issubdtype(xa.dtype, np.floating)
        yc = np.issubdtype(ya.dtype, np.floating)
        if xc and yc:
            method = "fisher_z"
        elif (not xc) and (not yc):
            method = "chi2"
        else:
            method = "mi"
    if method == "fisher_z":
        return fisher_z_test(xa, ya, z, **kw)
    if method == "chi2":
        return chi_square_ci(xa, ya, z, **kw)
    if method == "mi":
        return mutual_information_ci(xa, ya, z, **kw)
    raise ValueError(f"unknown CI method: {method}")


# ---------------------------------------------------------------------------
# backdoor criterion / identifiability audit
# ---------------------------------------------------------------------------
def _remove_outgoing(G: nx.DiGraph, x: str) -> nx.DiGraph:
    H = G.copy()
    H.remove_edges_from([(x, n) for n in list(G.successors(x))])
    return H


def _nodes_on_path(H: nx.DiGraph, x: str, y: str) -> set[str]:
    """Nodes lying on some undirected x-y path in H (superset of path nodes)."""
    Hu = H.to_undirected()
    if not nx.has_path(Hu, x, y):
        return set()
    out: set[str] = set()
    for v in list(Hu.nodes):
        if v in (x, y):
            continue
        H2 = Hu.copy()
        H2.remove_node(v)
        if not nx.has_path(H2, x, y):
            out.add(v)
    return out


def blocks_all_backdoor_paths(G: nx.DiGraph, x: str, y: str, Z: set[str]) -> bool:
    """True iff ``Z`` d-separates x and y in the graph with x's outgoing edges removed."""
    H = _remove_outgoing(G, x)
    return d_separated(H, x, y, Z)


def satisfies_backdoor(
    G: nx.DiGraph, x: str, y: str, Z: set[str], observed: set[str] | None = None
) -> bool:
    """Pearl's backdoor criterion: (i) no node in Z is a descendant of x,
    (ii) Z blocks all backdoor paths from x to y, (iii) all nodes in Z observed."""
    if any(n in set(nx.descendants(G, x)) for n in Z):
        return False
    if not blocks_all_backdoor_paths(G, x, y, Z):
        return False
    return observed is None or all(n in observed for n in Z)


def find_adjustment_set(
    G: nx.DiGraph, x: str, y: str, observed: set[str]
) -> list[str] | None:
    """Find a smallest *measured* set satisfying the backdoor criterion, else None.

    A minimal valid adjustment set only contains nodes on backdoor paths, so the
    search is restricted to observed nodes on x-y paths (bounded, exhaustive).
    """
    H = _remove_outgoing(G, x)
    desc_x = set(nx.descendants(G, x))
    on_path = _nodes_on_path(H, x, y)
    cand = [v for v in on_path if v in observed and v != x and v != y and v not in desc_x]
    cand.sort()
    for r in range(len(cand) + 1):
        for subset in itertools.combinations(cand, r):
            zset = set(subset)
            if blocks_all_backdoor_paths(G, x, y, zset):
                return list(subset)
    return None


def is_identifiable(G: nx.DiGraph, x: str, y: str, observed: set[str]) -> bool:
    """True iff the total causal effect of x on y is identifiable by a measured
    backdoor adjustment set."""
    return find_adjustment_set(G, x, y, observed) is not None


def counterfactual_identifiability_audit(
    G: nx.DiGraph,
    x: str,
    y: str,
    observed: set[str],
    assumptions: list[str] | None = None,
) -> dict[str, Any]:
    """Audit whether P(y | do(x)) is identifiable from the observed variables.

    Returns a dict with ``status`` ("identifiable" / "not_identifiable"), the
    ``adjustment_set`` (or None), and a ``reason`` naming the blocker.
    """
    adj = find_adjustment_set(G, x, y, observed)
    if adj is not None:
        status = "identifiable"
        reason = f"measured backdoor adjustment set {adj} blocks all backdoor paths"
    else:
        status = "not_identifiable"
        H = _remove_outgoing(G, x)
        pa_x = set(G.predecessors(x))
        if d_separated(H, x, y, pa_x):
            reason = (
                "unmeasured confounding: every backdoor-blocking set requires at least "
                "one unobserved node (e.g. a latent common cause of x and y)"
            )
        else:
            reason = "no backdoor set exists in the graph"
    return {
        "x": x,
        "y": y,
        "status": status,
        "adjustment_set": adj,
        "reason": reason,
        "assumptions": list(assumptions or []),
    }
