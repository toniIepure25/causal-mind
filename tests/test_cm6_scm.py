from __future__ import annotations

import json

import networkx as nx

from causal_mind.causal import (
    LABEL_ORDER,
    CandidateSCM,
    Edge,
    EdgeLabel,
    NodeSpec,
    NodeType,
)


def _sample_scm() -> CandidateSCM:
    m = CandidateSCM(name="toy")
    m.nodes["x"] = NodeSpec("x", NodeType.AFFECT, "affect state")
    m.nodes["y"] = NodeSpec("y", NodeType.SEMANTIC_STATE, "semantic state")
    m.nodes["u"] = NodeSpec("u", NodeType.LATENT_U, "latent confounder", observed=False)
    m.edges = [
        Edge("u", "x", EdgeLabel.ASSOCIATIONAL, "unmeasured common cause"),
        Edge("u", "y", EdgeLabel.ASSOCIATIONAL, "unmeasured common cause"),
        Edge("x", "y", EdgeLabel.TEMPORALLY_PRECEDENT, "x precedes y in time"),
    ]
    return m


def test_label_order_is_strictly_increasing() -> None:
    assert LABEL_ORDER[0] == EdgeLabel.NOT_IDENTIFIABLE
    assert LABEL_ORDER[-1] == EdgeLabel.CAUSALLY_IDENTIFIED
    assert len(set(LABEL_ORDER)) == len(LABEL_ORDER)


def test_node_and_edge_roundtrip_dict() -> None:
    m = _sample_scm()
    d = m.to_dict()
    m2 = CandidateSCM.from_dict(d)
    assert m2.name == m.name
    assert set(m2.nodes) == set(m.nodes)
    assert len(m2.edges) == len(m.edges)
    assert m2.edge("x", "y").label == EdgeLabel.TEMPORALLY_PRECEDENT
    assert m2.nodes["u"].observed is False


def test_json_roundtrip(tmp_path) -> None:
    m = _sample_scm()
    p = tmp_path / "scm.json"
    m.to_json(p)
    # valid JSON on disk
    json.loads(p.read_text())
    m2 = CandidateSCM.from_json(p)
    assert m2.to_dict() == m.to_dict()


def test_to_graph_and_dag() -> None:
    m = _sample_scm()
    g = m.to_graph()
    assert isinstance(g, nx.DiGraph)
    assert ("x", "y") in g.edges
    assert m.is_dag() is True


def test_post_init_adds_missing_nodes() -> None:
    m = CandidateSCM(name="n", edges=[Edge("a", "b", EdgeLabel.ASSOCIATIONAL, "j")])
    assert "a" in m.nodes and "b" in m.nodes


def test_set_edge_label_updates_and_adds() -> None:
    m = _sample_scm()
    m.set_edge_label("x", "y", EdgeLabel.CONDITIONALLY_SUPPORTED, "now supported")
    assert m.edge("x", "y").label == EdgeLabel.CONDITIONALLY_SUPPORTED
    m.set_edge_label("y", "x", EdgeLabel.NOT_IDENTIFIABLE, "reverse not id")
    assert m.edge("y", "x").label == EdgeLabel.NOT_IDENTIFIABLE


def test_label_counts() -> None:
    m = _sample_scm()
    counts = m.label_counts()
    assert counts["associational"] == 2
    assert counts["temporally_precedent"] == 1


def test_cycle_detected_not_dag() -> None:
    m = CandidateSCM(name="cyc")
    m.edges = [
        Edge("a", "b", EdgeLabel.ASSOCIATIONAL, ""),
        Edge("b", "a", EdgeLabel.ASSOCIATIONAL, ""),
    ]
    assert m.is_dag() is False


def test_node_type_taxonomy_complete() -> None:
    expected = {
        "semantic_state", "topic", "category", "affect", "sensory_modal",
        "goal_directedness", "memory_related", "control", "linguistic",
        "temporal", "previous_state", "latent_U",
    }
    assert {t.value for t in NodeType} == expected


def test_edge_label_taxonomy_complete() -> None:
    expected = {
        "associational", "temporally_precedent", "conditionally_supported",
        "causally_identified", "not_identifiable",
    }
    assert {t.value for t in EdgeLabel} == expected
