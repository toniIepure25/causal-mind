"""P(Future | do(X)) engine, v0.

The defining property of this module: it is IMPOSSIBLE to accidentally label an
unidentified counterfactual as causal. Every :class:`CounterfactualResult` carries
a ``counterfactual_status`` that is exactly one of::

    "observational_only"         -- conditional expectation from a fitted
                                    transition model; NOT a causal claim.
    "partially_identified"       -- identifiable from observational data under
                                    stated assumptions (a backdoor/adjustment
                                    proof is attached).
    "experimentally_identified"  -- supported by an attached randomized-evidence
                                    record; the ONLY status that may be read as
                                    a causal effect.

The API *refuses* (raises) if a caller tries to mark a result
``experimentally_identified`` without a valid :class:`RandomizedEvidence` record,
or ``partially_identified`` without an identifiability proof.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np

VALID_STATUSES: tuple[str, ...] = (
    "observational_only",
    "partially_identified",
    "experimentally_identified",
)


@dataclass
class RandomizedEvidence:
    """A record of randomized experimental evidence for an intervention effect."""

    experiment_id: str
    randomized: bool = True
    n: int = 0
    effect_estimate: float | None = None
    ci_low: float | None = None
    ci_high: float | None = None
    notes: str = ""

    def is_valid(self) -> bool:
        return bool(self.randomized) and self.n > 0


def _enforce(
    status: str, evidence: RandomizedEvidence | None, identifiability: dict | None
) -> None:
    """Raise unless ``status`` is supported by the attached evidence/proof."""
    if status not in VALID_STATUSES:
        msg = f"invalid counterfactual_status {status!r}; must be one of {VALID_STATUSES}"
        raise ValueError(msg)
    if status == "experimentally_identified" and (evidence is None or not evidence.is_valid()):
        raise ValueError(
            "refusing to mark a counterfactual 'experimentally_identified' "
            "without a valid RandomizedEvidence record (randomized=True, n>0)"
        )
    if status == "partially_identified" and (
        identifiability is None or identifiability.get("status") != "identifiable"
    ):
        raise ValueError(
            "refusing to mark a counterfactual 'partially_identified' "
            "without an identifiability proof (audit with status='identifiable')"
        )


@dataclass
class CounterfactualResult:
    """A P(Future | do(X)) estimate with an enforced causal-claim status."""

    estimand: str
    value: float | None
    counterfactual_status: str
    justification: str = ""
    evidence: RandomizedEvidence | None = None
    identifiability: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _enforce(self.counterfactual_status, self.evidence, self.identifiability)

    @property
    def is_causal_claim(self) -> bool:
        """Only an experimentally-identified result may be read as a causal effect."""
        return self.counterfactual_status == "experimentally_identified"


def observational_result(
    estimand: str,
    value: float | None,
    justification: str = "conditional expectation from a fitted transition model; not causal",
    identifiability: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> CounterfactualResult:
    """Build an ``observational_only`` result (the safe default)."""
    return CounterfactualResult(
        estimand=estimand,
        value=value,
        counterfactual_status="observational_only",
        justification=justification,
        evidence=None,
        identifiability=identifiability,
        metadata=metadata or {},
    )


class ObservationalSimulation:
    """Conditional expectation from a fitted transition model.

    This is a *simulation*, not a causal effect: it answers
    ``E[Future | X = a, history]`` under the fitted observational transition,
    with the incoming edges to ``X`` NOT severed. Results are always labelled
    ``observational_only``.
    """

    def __init__(
        self, transition_fn: Callable[..., np.ndarray], name: str = "observational"
    ) -> None:
        self.transition_fn = transition_fn
        self.name = name

    def simulate(
        self,
        estimand: str,
        x_value: Any,
        history: Any = None,
        summary: Callable[[np.ndarray], float] | None = None,
    ) -> CounterfactualResult:
        fut = np.asarray(self.transition_fn(x_value, history), dtype=float)
        value = float(summary(fut)) if summary is not None else float(np.mean(fut))
        return observational_result(
            estimand,
            value,
            justification=(
                f"E[Future | X={x_value!r}] under the fitted '{self.name}' transition model; "
                "observational conditional expectation, NOT a causal effect"
            ),
        )


class IdentifiedCounterfactual:
    """P(Future | do(X)) with an attached identifiability proof or randomized data.

    * With an identifiability audit (status='identifiable') -> ``partially_identified``.
    * With a valid :class:`RandomizedEvidence` record -> ``experimentally_identified``.
    * With neither -> raises (refuses to produce an unsupported causal claim).
    """

    def __init__(self, estimand: str) -> None:
        self.estimand = estimand

    def from_identifiability(
        self,
        value: float | None,
        audit: dict[str, Any],
        justification: str = "",
    ) -> CounterfactualResult:
        return CounterfactualResult(
            estimand=self.estimand,
            value=value,
            counterfactual_status="partially_identified",
            justification=justification or "identifiable by measured backdoor adjustment",
            evidence=None,
            identifiability=audit,
        )

    def from_experiment(
        self,
        value: float | None,
        evidence: RandomizedEvidence,
        justification: str = "",
        audit: dict[str, Any] | None = None,
    ) -> CounterfactualResult:
        return CounterfactualResult(
            estimand=self.estimand,
            value=value,
            counterfactual_status="experimentally_identified",
            justification=justification or "supported by randomized experimental evidence",
            evidence=evidence,
            identifiability=audit,
        )
