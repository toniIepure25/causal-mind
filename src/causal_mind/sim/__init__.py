"""CM-8R synthetic participant world (pre-human, no human data)."""
from causal_mind.sim.world import Scenario, TrialRecord, simulate_dataset, simulate_subject, true_ate
from causal_mind.sim import scenarios
from causal_mind.sim.estimator import ate_and_p, brp_by_condition

__all__ = [
    "Scenario", "TrialRecord", "simulate_dataset", "simulate_subject", "true_ate",
    "scenarios", "ate_and_p", "brp_by_condition",
]
