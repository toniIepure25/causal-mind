"""CM-9A: synthetic Oracle lab -- the thought world + oracle.

A synthetic agent has a mean-reverting thought stream x_t in R^D. An ORACLE can
intervene on the stream in four conditions:
  HIDDEN   -- the oracle shifts the state; the agent does NOT know.
  REVEAL   -- the oracle shifts the state AND signals it to the agent.
  VETO     -- the oracle blocks the agent's next thought (resets to a default).
  REDIRECT -- the oracle shifts the state to a specific new direction.

The agent responds according to a POLICY (O0-O10, see policies.py). This is a
purely synthetic exploration (no human data, no CM-8 confirmatory component).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class OracleCondition(str, Enum):
    HIDDEN = "hidden"
    REVEAL = "reveal"
    VETO = "veto"
    REDIRECT = "redirect"


@dataclass
class WorldConfig:
    dim: int = 32
    mu: float = 0.0
    phi: float = 0.7          # AR(1) persistence
    noise_sd: float = 0.5
    oracle_strength: float = 1.0   # magnitude of the oracle's shift
    veto_default: float = 0.0      # state the oracle resets to on a veto


@dataclass
class World:
    cfg: WorldConfig
    rng: np.random.Generator
    x: np.ndarray = field(init=False)
    t: int = field(default=0)

    def __post_init__(self) -> None:
        self.x = self.cfg.mu * np.ones(self.cfg.dim) + \
            self.rng.normal(0.0, self.cfg.noise_sd, size=self.cfg.dim)

    def _natural_step(self) -> np.ndarray:
        """The agent's natural (no-oracle) next thought."""
        return (self.cfg.mu + self.cfg.phi * (self.x - self.cfg.mu)
                + self.rng.normal(0.0, self.cfg.noise_sd, size=self.cfg.dim))

    def oracle_shift(self) -> np.ndarray:
        """The oracle's intervention vector (a random direction, scaled)."""
        d = self.rng.normal(size=self.cfg.dim)
        d /= (np.linalg.norm(d) + 1e-9)
        return self.cfg.oracle_strength * d

    def step(self, condition: OracleCondition, agent_response: np.ndarray) -> dict:
        """Advance one step. `agent_response` is the policy's contribution (added to the
        natural step). Returns the oracle signal the agent observes (None if hidden)."""
        natural = self._natural_step()
        signal = None
        if condition == OracleCondition.HIDDEN:
            self.x = natural + agent_response + self.oracle_shift()
            signal = None  # the agent does NOT know
        elif condition == OracleCondition.REVEAL:
            shift = self.oracle_shift()
            self.x = natural + agent_response + shift
            signal = shift  # the agent sees the shift
        elif condition == OracleCondition.VETO:
            # the oracle blocks the agent's next thought: reset to the default
            self.x = self.cfg.veto_default * np.ones(self.cfg.dim) + \
                self.rng.normal(0.0, 0.1, size=self.cfg.dim)
            signal = "veto"
        elif condition == OracleCondition.REDIRECT:
            shift = self.oracle_shift()
            self.x = natural * 0.3 + agent_response + shift  # strong redirect
            signal = shift
        else:  # pragma: no cover
            raise ValueError(f"unknown condition {condition}")
        self.t += 1
        return {"state": self.x.copy(), "signal": signal, "t": self.t}
