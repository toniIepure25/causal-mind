from __future__ import annotations

import itertools
import random

import networkx as nx
import numpy as np

from causal_mind.causal import (
    blocks_all_backdoor_paths,
    chi_square_ci,
    ci_test,
    counterfactual_identifiability_audit,
    d_connected,
    d_separated,
    find_adjustment_set,
    fisher_z_test,
    is_identifiable,
    mutual_information_ci,
)


def _dag(edges: list[tuple[str, str]]) -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g


# ---------------- d-separation on known DAGs ----------------
def test_chain_conditioning_blocks() -> None:
    G = _dag([("x", "m"), ("m", "y")])
    assert d_connected(G, "x", "y", set()) is True
    assert d_separated(G, "x", "y", {"m"}) is True


def test_collider_conditioning_opens() -> None:
    G = _dag([("x", "c"), ("y", "c")])
    assert d_separated(G, "x", "y", set()) is True
    assert d_connected(G, "x", "y", {"c"}) is True


def test_collider_descendant_opens() -> None:
    G = _dag([("x", "c"), ("y", "c"), ("c", "d")])
    assert d_separated(G, "x", "y", set()) is True
    assert d_connected(G, "x", "y", {"d"}) is True


def test_fork_conditioning_blocks() -> None:
    G = _dag([("m", "x"), ("m", "y")])
    assert d_connected(G, "x", "y", set()) is True
    assert d_separated(G, "x", "y", {"m"}) is True


def test_missing_node_is_separated() -> None:
    G = _dag([("a", "b")])
    assert d_separated(G, "a", "z", set()) is True


def _brute_d_connected(G: nx.DiGraph, x: str, y: str, Z: set[str]) -> bool:
    def active(path: list[str]) -> bool:
        for i in range(1, len(path) - 1):
            prev, node, nxt = path[i - 1], path[i], path[i + 1]
            collider = (prev, node) in G.edges and (nxt, node) in G.edges
            if collider:
                if not (node in Z or (set(nx.descendants(G, node)) & Z)):
                    return False
            elif node in Z:
                return False
        return True

    return any(active(p) for p in nx.all_simple_paths(G.to_undirected(), x, y))


def test_dsep_matches_bruteforce_on_random_dags() -> None:
    rng = random.Random(12345)
    for _ in range(60):
        n = rng.randint(3, 6)
        nodes = [f"n{i}" for i in range(n)]
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        perm = nodes[:]
        rng.shuffle(perm)
        idx = {v: i for i, v in enumerate(perm)}
        for a in nodes:
            for b in nodes:
                if a != b and idx[a] < idx[b] and rng.random() < 0.4:
                    G.add_edge(a, b)
        x, y = rng.sample(nodes, 2)
        for r in range(0, min(n, 3) + 1):
            for Z in itertools.combinations(nodes, r):
                Zs = set(Z)
                if x in Zs or y in Zs:
                    continue
                assert d_connected(G, x, y, Zs) == _brute_d_connected(G, x, y, Zs)


# ---------------- CI tests on synthetic data ----------------
def test_fisher_z_detects_dependence() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=2000)
    y = 0.8 * x + rng.normal(scale=0.4, size=2000)
    res = fisher_z_test(x, y)
    assert res["p"] < 0.01
    assert res["r_partial"] > 0.5


def test_fisher_z_independence_not_significant() -> None:
    rng = np.random.default_rng(1)
    x = rng.normal(size=3000)
    y = rng.normal(size=3000)
    res = fisher_z_test(x, y)
    assert res["p"] > 0.05


def test_fisher_z_conditional_independence_given_confounder() -> None:
    rng = np.random.default_rng(2)
    z = rng.normal(size=3000)
    x = z + rng.normal(scale=0.5, size=3000)
    y = z + rng.normal(scale=0.5, size=3000)
    assert fisher_z_test(x, y)["p"] < 0.01  # marginally dependent (confounded)
    assert fisher_z_test(x, y, z)["p"] > 0.05  # conditionally independent given z


def test_chi2_dependence_and_independence() -> None:
    rng = np.random.default_rng(3)
    n = 3000
    a = rng.integers(0, 3, size=n)
    b_dep = a % 2  # deterministic function of a -> dependent
    assert chi_square_ci(a, b_dep)["p"] < 0.01
    b_ind = rng.integers(0, 2, size=n)  # independent of a
    assert chi_square_ci(a, b_ind)["p"] > 0.05


def test_mutual_information_dependence_and_independence() -> None:
    rng = np.random.default_rng(4)
    n = 2000
    x = rng.normal(size=n)
    y_dep = x + rng.normal(scale=0.3, size=n)
    assert mutual_information_ci(x, y_dep, n_perm=100, seed=0)["p"] < 0.05
    y_ind = rng.normal(size=n)
    assert mutual_information_ci(x, y_ind, n_perm=100, seed=0)["p"] > 0.05


def test_ci_test_auto_dispatch() -> None:
    rng = np.random.default_rng(5)
    x = rng.normal(size=500)
    y = 0.5 * x + rng.normal(scale=0.5, size=500)
    res = ci_test(x, y, method="auto")
    assert "p" in res and "stat" in res


# ---------------- backdoor criterion / identifiability ----------------
def test_unmeasured_confounder_not_identifiable() -> None:
    G = _dag([("x", "a"), ("a", "y"), ("u", "x"), ("u", "y")])
    obs = {"x", "y", "a"}
    assert is_identifiable(G, "x", "y", obs) is False
    audit = counterfactual_identifiability_audit(G, "x", "y", obs)
    assert audit["status"] == "not_identifiable"
    assert audit["adjustment_set"] is None
    assert "unmeasured" in audit["reason"]


def test_measured_confounder_identifiable() -> None:
    G = _dag([("x", "a"), ("a", "y"), ("u", "x"), ("u", "y")])
    obs = {"x", "y", "a", "u"}
    assert is_identifiable(G, "x", "y", obs) is True
    adj = find_adjustment_set(G, "x", "y", obs)
    assert adj is not None and "u" in adj


def test_no_confounder_identifiable_with_empty_set() -> None:
    G = _dag([("x", "a"), ("a", "y")])
    obs = {"x", "y", "a"}
    assert is_identifiable(G, "x", "y", obs) is True
    assert find_adjustment_set(G, "x", "y", obs) == []


def test_adjustment_must_block_backdoor_not_causal_path() -> None:
    G = _dag([("x", "a"), ("a", "y"), ("u", "x"), ("u", "y")])
    assert blocks_all_backdoor_paths(G, "x", "y", {"a"}) is False
    assert blocks_all_backdoor_paths(G, "x", "y", {"u"}) is True


def test_descendant_of_x_cannot_be_in_adjustment_set() -> None:
    G = _dag([("x", "d"), ("d", "y"), ("u", "x"), ("u", "y")])
    obs = {"x", "y", "d", "u"}
    adj = find_adjustment_set(G, "x", "y", obs)
    assert adj is not None
    assert "d" not in adj
    assert "u" in adj
