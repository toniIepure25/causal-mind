import sys
sys.path.insert(0, "/home/jovyan/work/causal-mind-v2/src")
import networkx as nx
from causal_mind.causal import (
    d_separated, d_connected, CandidateSCM, Edge, EdgeLabel, NodeSpec, NodeType,
    find_adjustment_set, counterfactual_identifiability_audit, is_identifiable,
    Intervention, InterventionAction, apply_intervention,
    CounterfactualResult, RandomizedEvidence, IdentifiedCounterfactual,
    ObservationalSimulation, causal_trajectory_effect,
)

# --- d-separation on known DAGs ---
# chain: x -> m -> y
G = nx.DiGraph(); G.add_edges_from([("x", "m"), ("m", "y")])
assert d_connected(G, "x", "y", set()) is True, "chain unconditioned connected"
assert d_separated(G, "x", "y", {"m"}) is True, "chain conditioned on m separated"

# collider: x -> c <- y
G = nx.DiGraph(); G.add_edges_from([("x", "c"), ("y", "c")])
assert d_separated(G, "x", "y", set()) is True, "collider unconditioned separated"
assert d_connected(G, "x", "y", {"c"}) is True, "collider conditioned connected"
# conditioning on descendant of collider also opens
G = nx.DiGraph(); G.add_edges_from([("x", "c"), ("y", "c"), ("c", "d")])
assert d_connected(G, "x", "y", {"d"}) is True, "collider descendant opens"
assert d_separated(G, "x", "y", set()) is True

# fork: x <- m -> y
G = nx.DiGraph(); G.add_edges_from([("m", "x"), ("m", "y")])
assert d_connected(G, "x", "y", set()) is True
assert d_separated(G, "x", "y", {"m"}) is True

# complex: x -> a -> y, x <- u -> y (u unobserved confounder)
from causal_mind.causal import blocks_all_backdoor_paths
G = nx.DiGraph(); G.add_edges_from([("x", "a"), ("a", "y"), ("u", "x"), ("u", "y")])
assert d_connected(G, "x", "y", set()) is True
# the causal path x->a->y is active given {u} (a not conditioned) => d-connected
assert d_connected(G, "x", "y", {"u"}) is True
# adjusting on a does NOT block the backdoor path through u
assert blocks_all_backdoor_paths(G, "x", "y", {"a"}) is False
# adjusting on u blocks all backdoor paths (causal path removed by surgery)
assert blocks_all_backdoor_paths(G, "x", "y", {"u"}) is True
# conditioning on m in a chain blocks (all paths)
Gc = nx.DiGraph(); Gc.add_edges_from([("x", "m"), ("m", "y")])
assert d_separated(Gc, "x", "y", {"m"}) is True

print("d-separation OK")

# --- backdoor / identifiability ---
# u unobserved confounder: effect of x on y NOT identifiable from observed {x,y,a}
obs = {"x", "y", "a"}
G = nx.DiGraph(); G.add_edges_from([("x", "a"), ("a", "y"), ("u", "x"), ("u", "y")])
assert is_identifiable(G, "x", "y", obs) is False, "unmeasured confounder => not identifiable"
audit = counterfactual_identifiability_audit(G, "x", "y", obs)
assert audit["status"] == "not_identifiable", audit
print("audit (unmeasured):", audit["status"], "|", audit["reason"][:60])

# if u observed, identifiable by adjusting on u
obs2 = {"x", "y", "a", "u"}
assert is_identifiable(G, "x", "y", obs2) is True
adj = find_adjustment_set(G, "x", "y", obs2)
print("adjustment set (u observed):", adj)

# no confounder: x -> a -> y, identifiable with empty set
G2 = nx.DiGraph(); G2.add_edges_from([("x", "a"), ("a", "y")])
assert is_identifiable(G2, "x", "y", {"x", "y", "a"}) is True
adj2 = find_adjustment_set(G2, "x", "y", {"x", "y", "a"})
print("adjustment set (no confound):", adj2)

print("identifiability OK")

# --- interventions (graph surgery) ---
G = nx.DiGraph(); G.add_edges_from([("p1", "x"), ("p2", "x"), ("x", "y")])
H = apply_intervention(G, Intervention("x", InterventionAction.SET_VALUE, value=1.0))
assert ("p1", "x") not in H.edges and ("p2", "x") not in H.edges, "incoming edges severed"
assert ("x", "y") in H.edges, "outgoing edges kept"
assert H.nodes["x"]["do_value"] == 1.0
print("interventions OK")

# --- counterfactual status enforcement ---
# observational_only is always fine
r = CounterfactualResult("E[Y|do(X)]", 0.5, "observational_only")
assert r.counterfactual_status == "observational_only"
# experimentally_identified WITHOUT evidence must raise
try:
    CounterfactualResult("E[Y|do(X)]", 0.5, "experimentally_identified")
    raise AssertionError("should have raised")
except ValueError as e:
    print("refused no-evidence experimental:", str(e)[:50])
# experimentally_identified WITH valid evidence is fine
ev = RandomizedEvidence("exp1", randomized=True, n=100, effect_estimate=0.5)
r2 = CounterfactualResult("E[Y|do(X)]", 0.5, "experimentally_identified", evidence=ev)
assert r2.is_causal_claim
# partially_identified WITHOUT proof must raise
try:
    CounterfactualResult("E[Y|do(X)]", 0.5, "partially_identified")
    raise AssertionError("should have raised")
except ValueError as e:
    print("refused no-proof partial:", str(e)[:50])
# partially_identified WITH proof is fine
r3 = IdentifiedCounterfactual("E[Y|do(X)]").from_identifiability(
    0.5, {"status": "identifiable", "adjustment_set": ["u"]})
assert r3.counterfactual_status == "partially_identified"
print("counterfactual enforcement OK")

# --- metrics on synthetic signal ---
import numpy as np
rng = np.random.default_rng(0)
base = rng.normal(size=(50, 16))
fut_a = base + 0.1
fut_b = base + 5.0  # big shift
cte = causal_trajectory_effect(fut_a, fut_b)
assert cte.value > 4.0, cte.value
print("CTE:", round(cte.value, 3))

print("ALL SMOKE TESTS PASSED")
