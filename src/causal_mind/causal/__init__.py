"""causal_mind.causal -- candidate SCM, identifiability, interventions,
counterfactuals, and causal metrics for dynamic cognitive state (CM-6A).

Public API
----------
SCM spec        : CandidateSCM, NodeSpec, Edge, NodeType, EdgeLabel, LABEL_ORDER
Identifiability : d_separated, d_connected, ci_test, fisher_z_test, chi_square_ci,
                  mutual_information_ci, find_adjustment_set, is_identifiable,
                  counterfactual_identifiability_audit, satisfies_backdoor,
                  blocks_all_backdoor_paths
Interventions   : Intervention, InterventionAction, apply_intervention,
                  interventional_graph, incoming_edges_removed
Counterfactuals : CounterfactualResult, RandomizedEvidence, ObservationalSimulation,
                  IdentifiedCounterfactual, observational_result, VALID_STATUSES
Metrics         : causal_trajectory_effect, branch_redirection_probability,
                  trajectory_persistence, trajectory_divergence,
                  intervention_effect_decay, MetricResult
"""
from __future__ import annotations

from causal_mind.causal.counterfactuals import (
    VALID_STATUSES,
    CounterfactualResult,
    IdentifiedCounterfactual,
    ObservationalSimulation,
    RandomizedEvidence,
    observational_result,
)
from causal_mind.causal.identifiability import (
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
    satisfies_backdoor,
)
from causal_mind.causal.interventions import (
    Intervention,
    InterventionAction,
    apply_intervention,
    incoming_edges_removed,
    interventional_graph,
)
from causal_mind.causal.metrics import (
    MetricResult,
    branch_redirection_probability,
    causal_trajectory_effect,
    intervention_effect_decay,
    trajectory_divergence,
    trajectory_persistence,
)
from causal_mind.causal.scm import (
    LABEL_ORDER,
    CandidateSCM,
    Edge,
    EdgeLabel,
    NodeSpec,
    NodeType,
)

__all__ = [
    # scm
    "CandidateSCM",
    "NodeSpec",
    "Edge",
    "NodeType",
    "EdgeLabel",
    "LABEL_ORDER",
    # identifiability
    "d_separated",
    "d_connected",
    "ci_test",
    "fisher_z_test",
    "chi_square_ci",
    "mutual_information_ci",
    "find_adjustment_set",
    "is_identifiable",
    "counterfactual_identifiability_audit",
    "satisfies_backdoor",
    "blocks_all_backdoor_paths",
    # interventions
    "Intervention",
    "InterventionAction",
    "apply_intervention",
    "incoming_edges_removed",
    "interventional_graph",
    # counterfactuals
    "CounterfactualResult",
    "RandomizedEvidence",
    "ObservationalSimulation",
    "IdentifiedCounterfactual",
    "observational_result",
    "VALID_STATUSES",
    # metrics
    "MetricResult",
    "causal_trajectory_effect",
    "branch_redirection_probability",
    "trajectory_persistence",
    "trajectory_divergence",
    "intervention_effect_decay",
]
