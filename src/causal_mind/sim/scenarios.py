"""CM-8R2: the 21 data-generating scenarios (S0-S20).

Each is a :class:`~causal_mind.sim.world.Scenario` with explicit ground-truth causal
parameters. They are INDEPENDENT of the estimator's assumptions (they generate full
trajectories). See ``world.py`` for the dynamics.
"""
from __future__ import annotations

from causal_mind.sim.world import Scenario

# a "realistic" effect size for the active arms (home-point shift ~0.4 in error-norm units)
E = 0.4


def S0_TRUE_NULL() -> Scenario:
    return Scenario(name="S0_TRUE_NULL")


def S1_EXOGENOUS_ONLY() -> Scenario:
    return Scenario(name="S1_EXOGENOUS_ONLY", push_cue=E)


def S2_ENDOGENOUS_ONLY() -> Scenario:
    return Scenario(name="S2_ENDOGENOUS_ONLY", push_general=E)


def S3_BOTH_WORK() -> Scenario:
    return Scenario(name="S3_BOTH_WORK", push_general=E, push_cue=E)


def S4_IMMEDIATE_TRANSIENT() -> Scenario:
    # strong at h=1, rapid return -> at the frozen h*=2 the effect is mostly gone
    return Scenario(name="S4_IMMEDIATE_TRANSIENT", push_general=0.8, effect_duration=1)


def S5_PERSISTENT() -> Scenario:
    return Scenario(name="S5_PERSISTENT", push_general=E, effect_duration=64)


def S6_HETEROGENEOUS() -> Scenario:
    # 50% responders, 20% opposite, 30% non-responders
    return Scenario(name="S6_HETEROGENEOUS", push_general=0.6,
                    responder_frac=0.5, opposite_frac=0.2)


def S7_HIGH_ICC() -> Scenario:
    return Scenario(name="S7_HIGH_ICC", push_general=E, subject_push_sd=1.0)


def S8_FATIGUE() -> Scenario:
    return Scenario(name="S8_FATIGUE", push_general=0.6, fatigue=1.5)


def S9_LEARNING() -> Scenario:
    return Scenario(name="S9_LEARNING", push_general=0.2, learning=1.5)


def S10_SHAM_EFFECT() -> Scenario:
    return Scenario(name="S10_SHAM_EFFECT", push_general=E, push_sham=0.3)


def S11_LEXICAL_PRIMING() -> Scenario:
    return Scenario(name="S11_LEXICAL_PRIMING", push_cue=0.6, priming_transient=True)


def S12_MNAR() -> Scenario:
    return Scenario(name="S12_MNAR", push_general=E, mnar=True)


def S13_FORECAST_ERROR() -> Scenario:
    return Scenario(name="S13_FORECAST_ERROR", push_general=E, forecast_bias=0.6)


def S14_VOLATILITY() -> Scenario:
    return Scenario(name="S14_VOLATILITY", push_general=E, sigma=2.0)


def S15_STRATEGIC() -> Scenario:
    return Scenario(name="S15_STRATEGIC", push_general=E, strategic=True)


def S16_CONDITION_LEARNING() -> Scenario:
    return Scenario(name="S16_CONDITION_LEARNING", push_general=E, condition_learning=True)


def S17_DELAYED() -> Scenario:
    return Scenario(name="S17_DELAYED", push_general=E, delayed_start=3)


def S18_RETURN() -> Scenario:
    return Scenario(name="S18_RETURN", push_general=E, return_dynamics=True)


def S19_CROSSOVER() -> Scenario:
    return Scenario(name="S19_CROSSOVER", push_general=E, crossover=True)


def S20_STATE_DEPENDENT() -> Scenario:
    return Scenario(name="S20_STATE_DEPENDENT", push_general=E, state_dependent=True)


ALL_SCENARIOS = {
    "S0": S0_TRUE_NULL, "S1": S1_EXOGENOUS_ONLY, "S2": S2_ENDOGENOUS_ONLY,
    "S3": S3_BOTH_WORK, "S4": S4_IMMEDIATE_TRANSIENT, "S5": S5_PERSISTENT,
    "S6": S6_HETEROGENEOUS, "S7": S7_HIGH_ICC, "S8": S8_FATIGUE,
    "S9": S9_LEARNING, "S10": S10_SHAM_EFFECT, "S11": S11_LEXICAL_PRIMING,
    "S12": S12_MNAR, "S13": S13_FORECAST_ERROR, "S14": S14_VOLATILITY,
    "S15": S15_STRATEGIC, "S16": S16_CONDITION_LEARNING, "S17": S17_DELAYED,
    "S18": S18_RETURN, "S19": S19_CROSSOVER, "S20": S20_STATE_DEPENDENT,
}
