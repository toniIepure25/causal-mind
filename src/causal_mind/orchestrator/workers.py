from __future__ import annotations

WORKERS: tuple[str, ...] = (
    "researcher",
    "data",
    "forecasting",
    "causal",
    "reviewer",
)

ALL_ROLES: tuple[str, ...] = ("orchestrator", *WORKERS)

WORKER_AGENT_NAMES: dict[str, str] = {
    "orchestrator": "orchestrator",
    "researcher": "researcher",
    "data": "data-engineer",
    "forecasting": "forecasting-engineer",
    "causal": "causal-engineer",
    "reviewer": "reviewer",
}
