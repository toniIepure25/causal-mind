from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TaskState = Literal["queue", "running", "review", "done", "blocked", "killed"]
ResourceClass = Literal["cpu", "gpu-light", "gpu-exclusive"]


class TaskSpec(BaseModel):
    id: str
    title: str
    hypothesis: str | None = None
    objective: str
    owner: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    resource_class: ResourceClass = "cpu"
    expected_runtime: str | None = None
    allowed_paths: list[str] = Field(default_factory=list)
    forbidden_paths: list[str] = Field(default_factory=list)
    required_tests: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    failure_criteria: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=list)
    assigned_worker: str | None = None
    state: TaskState = "queue"
