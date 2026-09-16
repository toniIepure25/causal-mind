"""Structural Causal Model (SCM) specification for dynamic cognitive state.

This module defines the *candidate* SCM used by CM-6A. It is deliberately a
specification/serialization layer: it names the nodes of a dynamic cognitive
state, the directed edges between them, and a label taxonomy that records how
much causal support each edge has. It does NOT assert that any edge is causal;
the label taxonomy exists precisely to keep observational association distinct
from causal identification.

A candidate SCM is a DAG over time-indexed cognitive-state variables plus an
explicit unmeasured-confounder node (``latent_U``). The structural equations
are of the form::

    Z[t+1] = f(Z[t], Z[t-1:t-k], context[t], latent_U[t])

where ``Z`` is the vector of cognitive-state dimensions.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

import networkx as nx


class NodeType(StrEnum):
    """Taxonomy of node kinds in the dynamic cognitive-state SCM."""

    SEMANTIC_STATE = "semantic_state"
    TOPIC = "topic"
    CATEGORY = "category"
    AFFECT = "affect"
    SENSORY_MODAL = "sensory_modal"
    GOAL_DIRECTEDNESS = "goal_directedness"
    MEMORY_RELATED = "memory_related"
    CONTROL = "control"
    LINGUISTIC = "linguistic"
    TEMPORAL = "temporal"
    PREVIOUS_STATE = "previous_state"
    LATENT_U = "latent_U"


class EdgeLabel(StrEnum):
    """How much causal support a directed edge has.

    The labels are ordered by increasing strength of causal claim. An edge's
    label is a *claim level*: it records what the evidence supports, never more.
    """

    ASSOCIATIONAL = "associational"
    TEMPORALLY_PRECEDENT = "temporally_precedent"
    CONDITIONALLY_SUPPORTED = "conditionally_supported"
    CAUSALLY_IDENTIFIED = "causally_identified"
    NOT_IDENTIFIABLE = "not_identifiable"


#: Strictly increasing order of causal-claim strength (for comparisons/sorting).
LABEL_ORDER: tuple[EdgeLabel, ...] = (
    EdgeLabel.NOT_IDENTIFIABLE,
    EdgeLabel.ASSOCIATIONAL,
    EdgeLabel.TEMPORALLY_PRECEDENT,
    EdgeLabel.CONDITIONALLY_SUPPORTED,
    EdgeLabel.CAUSALLY_IDENTIFIED,
)


@dataclass
class NodeSpec:
    """A single node in the candidate SCM."""

    name: str
    node_type: NodeType
    description: str = ""
    observed: bool = True
    time_indexed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "node_type": self.node_type.value,
            "description": self.description,
            "observed": self.observed,
            "time_indexed": self.time_indexed,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> NodeSpec:
        return cls(
            name=d["name"],
            node_type=NodeType(d["node_type"]),
            description=d.get("description", ""),
            observed=d.get("observed", True),
            time_indexed=d.get("time_indexed", True),
        )


@dataclass
class Edge:
    """A directed edge ``src -> dst`` with a causal-claim label.

    Every edge carries exactly one :class:`EdgeLabel` and a human-readable
    ``justification`` explaining why that label was assigned.
    """

    src: str
    dst: str
    label: EdgeLabel
    justification: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "src": self.src,
            "dst": self.dst,
            "label": self.label.value,
            "justification": self.justification,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Edge:
        return cls(
            src=d["src"],
            dst=d["dst"],
            label=EdgeLabel(d["label"]),
            justification=d.get("justification", ""),
            metadata=d.get("metadata", {}),
        )


@dataclass
class CandidateSCM:
    """A candidate structural causal model over dynamic cognitive state.

    Attributes
    ----------
    name:
        Human-readable model name.
    nodes:
        Mapping of node name -> :class:`NodeSpec`.
    edges:
        List of :class:`Edge`.
    structural_equation:
        Symbolic description of the transition, e.g.
        ``"Z[t+1] = f(Z[t], Z[t-1:t-k], context[t], latent_U[t])"``.
    assumptions:
        Free-text list of identification assumptions the model relies on.
    """

    name: str
    nodes: dict[str, NodeSpec] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    structural_equation: str = "Z[t+1] = f(Z[t], Z[t-1:t-k], context[t], latent_U[t])"
    assumptions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        for e in self.edges:
            if e.src not in self.nodes:
                self.nodes[e.src] = NodeSpec(e.src, NodeType.SEMANTIC_STATE)
            if e.dst not in self.nodes:
                self.nodes[e.dst] = NodeSpec(e.dst, NodeType.SEMANTIC_STATE)

    # -- graph view ---------------------------------------------------------
    def to_graph(self) -> nx.DiGraph:
        """Return the SCM as a :class:`networkx.DiGraph` (nodes + directed edges)."""
        g = nx.DiGraph()
        for name, spec in self.nodes.items():
            g.add_node(name, **spec.to_dict())
        for e in self.edges:
            g.add_edge(e.src, e.dst, label=e.label.value, justification=e.justification)
        return g

    def is_dag(self) -> bool:
        return nx.is_directed_acyclic_graph(self.to_graph())

    # -- edge lookup --------------------------------------------------------
    def edge(self, src: str, dst: str) -> Edge | None:
        for e in self.edges:
            if e.src == src and e.dst == dst:
                return e
        return None

    def set_edge_label(self, src: str, dst: str, label: EdgeLabel, justification: str) -> None:
        e = self.edge(src, dst)
        if e is None:
            self.edges.append(Edge(src, dst, label, justification))
        else:
            e.label = label
            e.justification = justification

    def label_counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for e in self.edges:
            out[e.label.value] = out.get(e.label.value, 0) + 1
        return out

    # -- serialization ------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "structural_equation": self.structural_equation,
            "assumptions": list(self.assumptions),
            "nodes": [s.to_dict() for s in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CandidateSCM:
        m = cls(
            name=d["name"],
            structural_equation=d.get("structural_equation", cls.structural_equation),
            assumptions=list(d.get("assumptions", [])),
        )
        for nd in d.get("nodes", []):
            spec = NodeSpec.from_dict(nd)
            m.nodes[spec.name] = spec
        for ed in d.get("edges", []):
            m.edges.append(Edge.from_dict(ed))
        return m

    def to_json(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def from_json(cls, path: str | Path) -> CandidateSCM:
        return cls.from_dict(json.loads(Path(path).read_text()))
