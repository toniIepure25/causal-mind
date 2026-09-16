from __future__ import annotations

import networkx as nx
import numpy as np
import pytest

from causal_mind.causal import (
    CounterfactualResult,
    IdentifiedCounterfactual,
    Intervention,
    InterventionAction,
    ObservationalSimulation,
    RandomizedEvidence,
    apply_intervention,
    incoming_edges_removed,
    interventional_graph,
    observational_result,
)


def _dag(edges: list[tuple[str, str]]) -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_edges_from(edges)
    return g


# ---------------- do(X) graph surgery ----------------
def test_do_x_removes_incoming_keeps_outgoing() -> None:
    G = _dag([("p1", "x"), ("p2", "x"), ("x", "y")])
    H = apply_intervention(G, Intervention("x", InterventionAction.SET_VALUE, value=1.0))
    assert ("p1", "x") not in H.edges
    assert ("p2", "x") not in H.edges
    assert ("x", "y") in H.edges
    assert H.nodes["x"]["do_value"] == 1.0
    assert incoming_edges_removed(G, H, "x") is True
    assert ("p1", "x") in G.edges  # original graph untouched


def test_remove_incoming_action() -> None:
    G = _dag([("p", "x"), ("x", "y")])
    H = apply_intervention(G, Intervention("x", InterventionAction.REMOVE_INCOMING))
    assert ("p", "x") not in H.edges
    assert ("x", "y") in H.edges
    assert "do_value" not in H.nodes["x"]


def test_intervention_on_missing_node_raises() -> None:
    G = _dag([("a", "b")])
    with pytest.raises(KeyError):
        apply_intervention(G, Intervention("zzz"))


def test_multiple_interventions() -> None:
    G = _dag([("p", "x"), ("x", "y"), ("y", "z")])
    H = interventional_graph(G, [
        Intervention("x", InterventionAction.SET_VALUE, value=0.0),
        Intervention("z", InterventionAction.CLAMP, value=2.0),
    ])
    assert ("p", "x") not in H.edges  # x intervened: incoming severed
    assert ("x", "y") in H.edges  # x's outgoing edge kept
    assert ("y", "z") not in H.edges  # z intervened: incoming severed
    assert H.nodes["z"]["do_value"] == 2.0


# ---------------- counterfactual status enforcement ----------------
def test_observational_only_always_allowed() -> None:
    r = CounterfactualResult("E[Y|do(X)]", 0.5, "observational_only")
    assert r.counterfactual_status == "observational_only"
    assert r.is_causal_claim is False


def test_invalid_status_raises() -> None:
    with pytest.raises(ValueError):
        CounterfactualResult("E[Y|do(X)]", 0.5, "definitely_causal")


def test_experimentally_identified_without_evidence_raises() -> None:
    with pytest.raises(ValueError, match="experimentally_identified"):
        CounterfactualResult("E[Y|do(X)]", 0.5, "experimentally_identified")


def test_experimentally_identified_with_invalid_evidence_raises() -> None:
    ev = RandomizedEvidence("exp", randomized=True, n=0)  # n=0 -> invalid
    with pytest.raises(ValueError):
        CounterfactualResult("E[Y|do(X)]", 0.5, "experimentally_identified", evidence=ev)


def test_experimentally_identified_with_valid_evidence_ok() -> None:
    ev = RandomizedEvidence("exp1", randomized=True, n=100, effect_estimate=0.5)
    r = CounterfactualResult("E[Y|do(X)]", 0.5, "experimentally_identified", evidence=ev)
    assert r.is_causal_claim is True


def test_partially_identified_without_proof_raises() -> None:
    with pytest.raises(ValueError, match="partially_identified"):
        CounterfactualResult("E[Y|do(X)]", 0.5, "partially_identified")


def test_partially_identified_with_nonidentifiable_audit_raises() -> None:
    audit = {"status": "not_identifiable", "adjustment_set": None}
    with pytest.raises(ValueError):
        CounterfactualResult("E[Y|do(X)]", 0.5, "partially_identified", identifiability=audit)


def test_partially_identified_with_proof_ok() -> None:
    audit = {"status": "identifiable", "adjustment_set": ["u"]}
    r = IdentifiedCounterfactual("E[Y|do(X)]").from_identifiability(0.5, audit)
    assert r.counterfactual_status == "partially_identified"
    assert r.is_causal_claim is False


def test_from_experiment_requires_valid_evidence() -> None:
    icf = IdentifiedCounterfactual("E[Y|do(X)]")
    with pytest.raises(ValueError):
        icf.from_experiment(0.5, RandomizedEvidence("e", randomized=False, n=10))
    r = icf.from_experiment(0.5, RandomizedEvidence("e", randomized=True, n=10))
    assert r.is_causal_claim is True


# ---------------- engines ----------------
def test_observational_simulation_labelled_not_causal() -> None:
    def transition(x_value, history):
        return np.array([1.0 + x_value, 2.0 + x_value, 3.0 + x_value])

    sim = ObservationalSimulation(transition, name="linear")
    r = sim.simulate("E[Y|X=1]", x_value=1.0)
    assert r.counterfactual_status == "observational_only"
    assert r.is_causal_claim is False
    assert r.value == pytest.approx(3.0)  # mean of [2,3,4]


def test_observational_result_helper() -> None:
    r = observational_result("E[Y|X=a]", 0.25)
    assert r.counterfactual_status == "observational_only"
    assert "not causal" in r.justification.lower() or "observational" in r.justification.lower()
