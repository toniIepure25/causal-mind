"""do(X) intervention machinery on the candidate SCM.

An intervention ``do(X)`` performs *graph surgery*: it severs every incoming
edge to ``X`` so that ``X`` is no longer a function of its parents (Pearl's
intervention). Interventions are represented as dataclasses and applied to a
:class:`networkx.DiGraph` to produce the interventional graph.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import networkx as nx


class InterventionAction(StrEnum):
    """Kind of intervention applied to a node."""

    SET_VALUE = "set_value"
    REMOVE_INCOMING = "remove_incoming"
    CLAMP = "clamp"


@dataclass
class Intervention:
    """A single intervention on node ``node``.

    * ``SET_VALUE``: fix the node to ``value`` (sever incoming edges, set constant).
    * ``CLAMP``: hold the node at ``value`` over time (sever incoming edges).
    * ``REMOVE_INCOMING``: sever incoming edges only (node becomes exogenous,
      its own dynamics / noise remain).
    """

    node: str
    action: InterventionAction = InterventionAction.SET_VALUE
    value: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def severs_incoming(self) -> bool:
        return self.action in (
            InterventionAction.SET_VALUE,
            InterventionAction.CLAMP,
            InterventionAction.REMOVE_INCOMING,
        )


def apply_intervention(G: nx.DiGraph, iv: Intervention) -> nx.DiGraph:
    """Return a copy of ``G`` with the graph surgery for ``iv`` applied.

    All three action types sever the incoming edges to ``iv.node`` (the defining
    operation of ``do(X)``). ``SET_VALUE`` / ``CLAMP`` additionally record the
    fixed value on the node attribute.
    """
    H = G.copy()
    if iv.node not in H:
        raise KeyError(f"intervention node {iv.node!r} not in graph")
    if iv.severs_incoming():
        H.remove_edges_from([(p, iv.node) for p in list(H.predecessors(iv.node))])
    if iv.action in (InterventionAction.SET_VALUE, InterventionAction.CLAMP):
        H.nodes[iv.node]["do_value"] = iv.value
        H.nodes[iv.node]["do_action"] = iv.action.value
    else:
        H.nodes[iv.node]["do_action"] = iv.action.value
    return H


def interventional_graph(G: nx.DiGraph, interventions: list[Intervention]) -> nx.DiGraph:
    """Apply a list of interventions (sequentially) to ``G``."""
    H = G
    for iv in interventions:
        H = apply_intervention(H, iv)
    return H


def incoming_edges_removed(G: nx.DiGraph, H: nx.DiGraph, node: str) -> bool:
    """True iff every incoming edge to ``node`` in ``G`` is absent in ``H``."""
    return all((p, node) not in H.edges for p in G.predecessors(node))
