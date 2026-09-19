"""CM-8R2: synthetic participant world (independent generative simulator).

An independent generative model of the CM-8 experiment. It is NOT built to reproduce
the estimator's assumptions: it generates full semantic trajectories, applies the
randomization and the intervention as a real perturbation of the dynamics, and exposes
ground-truth causal parameters so estimator recovery can be measured.

Core dynamics (per subject):
  * a "home" semantic region ``home`` (d-dim);
  * a mean-reverting AR(1) trajectory  z_t = home + phi*(z_{t-1}-home) + sigma*eps_t;
  * a FROZEN predictor: the h*-step AR(1) forecast  F_t = home + phi^h*(z_t - home)
    (the best linear forecast; the forecast-error scenario S13 adds a bias);
  * the predicted basin: a ball of radius r_alpha around F_t, where r_alpha is the
    (1-basin_tail) quantile of the held-out natural prediction-error norm;
  * BRP: the fraction of post-intervention states outside the basin.

An intervention (GENERAL/CUE) shifts the home point by a condition-specific ``delta``
for ``effect_duration`` steps after the intervention; the AR(1) impulse response gives
the shift of the future state at horizon h* as  delta*(1 - phi^h*).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Scenario:
    """A data-generating process. Every field is a ground-truth causal parameter."""
    name: str = "S0_TRUE_NULL"
    # natural dynamics
    d: int = 32
    phi: float = 0.80          # persistence (AR(1) coefficient, 0-1)
    sigma: float = 1.0         # innovation noise
    # intervention home-point shift magnitudes (the redirection effect)
    push_general: float = 0.0
    push_cue: float = 0.0
    push_sham: float = 0.0
    # how many steps the home shift persists (1 = transient, large = persistent)
    effect_duration: int = 8
    # heterogeneity (fraction of subjects that are responders / opposite responders)
    responder_frac: float = 1.0
    opposite_frac: float = 0.0
    subject_push_sd: float = 0.0   # S7: between-subject SD of the push (drives ICC)
    # trial-index modulation (trial_frac in [0,1])
    fatigue: float = 0.0       # effect scaled by (1 - fatigue*trial_frac)
    learning: float = 0.0      # effect scaled by (1 + learning*trial_frac)
    # confounds
    priming_transient: bool = False   # S11: cue effect vanishes by h>=2 (lexical echo)
    mnar: bool = False                # S12: missing when the effect is large
    forecast_bias: float = 0.0        # S13: predictor is wrong (bias in the forecast)
    strategic: bool = False           # S15: participant games the intervention
    condition_learning: bool = False  # S16: participant infers the randomization
    delayed_start: int = 0            # S17: effect begins after this many steps
    return_dynamics: bool = False     # S18: leaves then returns (oscillatory)
    crossover: bool = False           # S19: pushes toward an unintended basin
    state_dependent: bool = False     # S20: effect depends on pre-intervention state
    # analysis
    basin_tail: float = 0.10
    h_star: int = 2

    def push_for(self, condition: str) -> float:
        return {"control": 0.0, "sham": self.push_sham,
                "general": self.push_general, "cue": self.push_cue}[condition]


CONDITIONS = ("control", "sham", "general", "cue")


def _ar1_step(z: np.ndarray, home: np.ndarray, phi: float, sigma: float,
              rng: np.random.Generator) -> np.ndarray:
    return home + phi * (z - home) + sigma * rng.normal(size=z.shape)


def _natural_error_norms(home: np.ndarray, phi: float, sigma: float, d: int, h: int,
                         n: int, rng: np.random.Generator) -> np.ndarray:
    """Held-out natural prediction-error norms (for the basin radius)."""
    norms = np.empty(n)
    z = home + rng.normal(size=d) * (sigma / np.sqrt(1 - phi * phi))
    for i in range(n):
        # forecast from z at horizon h, then advance h steps
        F = home + (phi ** h) * (z - home)
        zz = z
        for _ in range(h):
            zz = _ar1_step(zz, home, phi, sigma, rng)
        norms[i] = np.linalg.norm(zz - F)
        z = zz
    return norms


def _impulse_response(delta: float, phi: float, h: int, duration: int,
                      delayed: int, return_dyn: bool) -> float:
    """Shift of the future state at horizon h from a home-point step of size delta."""
    if h < delayed:
        return 0.0
    if h > duration:
        return 0.0
    resp = delta * (1.0 - phi ** h)
    if return_dyn and h >= 2:
        resp *= (1.0 - 0.5 * (h - 1))  # partial return after the first step
    return max(resp, 0.0) if resp > 0 else resp


@dataclass
class TrialRecord:
    subject: int
    trial: int
    condition: str
    leave: int
    error_norm: float
    true_effect: float   # ground-truth BRP contribution of the intervention


def simulate_subject(sc: Scenario, n_trials: int, rng: np.random.Generator,
                     seed_subject: int = 0) -> list[TrialRecord]:
    """Simulate one subject's trials under scenario ``sc``."""
    d = sc.d
    home = rng.normal(size=d)
    # subject-level responder / opposite assignment (S6, S20)
    u = rng.random()
    if u < sc.opposite_frac:
        subj_mult = -1.0
    elif u < sc.opposite_frac + sc.responder_frac:
        subj_mult = 1.0
    else:
        subj_mult = 0.0  # non-responder
    # between-subject push variability (S7, drives ICC)
    if sc.subject_push_sd > 0:
        subj_mult = subj_mult * float(np.exp(rng.normal(0.0, sc.subject_push_sd)))
    # basin radius from held-out natural errors (no intervention data)
    norms = _natural_error_norms(home, sc.phi, sc.sigma, d, sc.h_star, 4000, rng)
    r_alpha = float(np.quantile(norms, 1.0 - sc.basin_tail))

    # a long running trajectory (the "session")
    z = home + rng.normal(size=d) * (sc.sigma / np.sqrt(1 - sc.phi * sc.phi))
    # randomization: within-subject, counterbalanced-ish (random per trial)
    recs: list[TrialRecord] = []
    for t in range(n_trials):
        cond = CONDITIONS[rng.integers(0, 4)]
        trial_frac = t / max(1, n_trials - 1)
        # forecast from the current state (frozen predictor)
        F = home + (sc.phi ** sc.h_star) * (z - home)
        if sc.forecast_bias:
            F = F + sc.forecast_bias * rng.normal(size=d)  # S13: wrong forecast
        # advance h* steps under the NATURAL dynamics to get the baseline future
        z_nat = z
        for _ in range(sc.h_star):
            z_nat = _ar1_step(z_nat, home, sc.phi, sc.sigma, rng)
        # apply the intervention: a home-point shift for effect_duration steps
        delta = sc.push_for(cond) * subj_mult
        mod = (1.0 - sc.fatigue * trial_frac) * (1.0 + sc.learning * trial_frac)
        if sc.state_dependent:
            mod = mod * (0.5 + 0.5 * np.linalg.norm(z - home))  # S20
        if sc.strategic:
            mod = mod * (1.0 + 0.5 * (cond in ("general", "cue")))  # S15
        if sc.priming_transient and cond == "cue":
            dur = 1  # S11: lexical echo vanishes by h>=2
        else:
            dur = sc.effect_duration
        shift = _impulse_response(delta * mod, sc.phi, sc.h_star, dur,
                                  sc.delayed_start, sc.return_dynamics)
        # the actual future state = natural future + the intervention shift (direction)
        if abs(shift) > 1e-12:
            direction = (z_nat - F)
            nd = np.linalg.norm(direction)
            if nd < 1e-9:
                direction = rng.normal(size=d)
                nd = np.linalg.norm(direction)
            direction = direction / nd
            if sc.crossover:  # S19: push toward an unintended direction
                direction = -direction
            z_future = z_nat + shift * direction
        else:
            z_future = z_nat
        err = np.linalg.norm(z_future - F)
        leave = int(err > r_alpha)
        # MNAR: drop the trial (record as missing) when the effect is large (S12)
        if sc.mnar and rng.random() < 0.3 * (err > r_alpha):
            recs.append(TrialRecord(seed_subject, t, cond, -1, float("nan"), shift))
        else:
            recs.append(TrialRecord(seed_subject, t, cond, leave, float(err), shift))
        z = z_future  # continue the session from the realized future
    return recs


def simulate_dataset(sc: Scenario, n_subjects: int, n_trials: int,
                     seed: int = 20260917) -> list[TrialRecord]:
    rng = np.random.default_rng(seed)
    recs: list[TrialRecord] = []
    for s in range(n_subjects):
        recs.extend(simulate_subject(sc, n_trials, rng, seed_subject=s))
    return recs


def true_ate(sc: Scenario, arm: str, n_subjects: int = 400, n_trials: int = 60,
             seed: int = 0) -> float:
    """Ground-truth ATE (BRP difference) for ``arm`` vs pooled control/sham, computed
    directly from the DGP (large-sample, no estimator)."""
    def _brp(push_arm: float):
        sc2 = Scenario(**{**sc.__dict__, "push_general": (push_arm if arm == "general" else sc.push_general),
                          "push_cue": (push_arm if arm == "cue" else sc.push_cue)})
        rng = np.random.default_rng(seed)
        leaves, total = 0, 0
        for _ in range(n_subjects):
            for r in simulate_subject(sc2, n_trials, rng):
                if r.leave >= 0 and sc.push_for(r.condition) == 0.0 and r.condition in ("control", "sham"):
                    leaves += r.leave
                    total += 1
        # intervention arm BRP
        rng = np.random.default_rng(seed + 1)
        lev, tot = 0, 0
        for _ in range(n_subjects):
            for r in simulate_subject(sc2, n_trials, rng):
                if r.leave >= 0 and r.condition == arm:
                    lev += r.leave
                    tot += 1
        return (lev / tot if tot else 0.0) - (leaves / total if total else 0.0)
    return _brp(sc.push_for(arm))
