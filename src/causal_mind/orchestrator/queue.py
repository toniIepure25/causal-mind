from __future__ import annotations

import shutil
from pathlib import Path

import yaml
from pydantic import ValidationError

from causal_mind.orchestrator.models import TaskSpec, TaskState

STATE_DIRS: tuple[TaskState, ...] = ("queue", "running", "review", "done", "blocked", "killed")


class TaskQueue:
    """Filesystem task queue with atomic claims.

    A task exists in exactly one state directory. Claiming is a rename from
    ``queue/`` to ``running/``; a lost race observes the missing file and moves on.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        for state in STATE_DIRS:
            (root / state).mkdir(parents=True, exist_ok=True)

    def register(self, path: Path) -> TaskSpec:
        task = self._read(path)
        task.state = "queue"
        target = self.root / "queue" / f"{task.id}.yaml"
        self._write(target, task)
        return task

    def list_tasks(self) -> list[TaskSpec]:
        tasks: list[TaskSpec] = []
        for state in STATE_DIRS:
            for path in sorted((self.root / state).glob("*.yaml")):
                task = self._try_read(path)
                if task is None:
                    continue
                task.state = state
                tasks.append(task)
        return tasks

    def count_by_state(self) -> dict[str, int]:
        return {state: len(list((self.root / state).glob("*.yaml"))) for state in STATE_DIRS}

    def done_ids(self) -> set[str]:
        ids: set[str] = set()
        for path in (self.root / "done").glob("*.yaml"):
            task = self._try_read(path)
            if task is not None:
                ids.add(task.id)
        return ids

    def assign(self, task_id: str, worker: str) -> TaskSpec:
        path = self._find(task_id)
        task = self._read(path)
        task.assigned_worker = worker
        self._write(path, task)
        return task

    def claim_next(self, worker: str) -> TaskSpec | None:
        done = self.done_ids()
        for path in sorted((self.root / "queue").glob("*.yaml")):
            task = self._try_read(path)
            if task is None:
                continue
            if task.assigned_worker is not None and task.assigned_worker != worker:
                continue
            if any(dependency not in done for dependency in task.dependencies):
                continue

            target = self.root / "running" / path.name
            try:
                path.replace(target)
            except FileNotFoundError:
                continue

            task.state = "running"
            if task.assigned_worker is None:
                task.assigned_worker = worker
            self._write(target, task)
            return task
        return None

    def transition(self, task_id: str, state: TaskState) -> TaskSpec:
        current = self._find(task_id)
        task = self._read(current)
        task.state = state
        if state == "queue":
            task.assigned_worker = None
        target = self.root / state / current.name
        if current.resolve() != target.resolve():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current), str(target))
        self._write(target, task)
        return task

    def _find(self, task_id: str) -> Path:
        for state in STATE_DIRS:
            direct = self.root / state / f"{task_id}.yaml"
            if direct.exists():
                return direct
            for path in sorted((self.root / state).glob("*.yaml")):
                task = self._try_read(path)
                if task is not None and task.id == task_id:
                    return path
        raise FileNotFoundError(task_id)

    def _try_read(self, path: Path) -> TaskSpec | None:
        try:
            return self._read(path)
        except (FileNotFoundError, OSError, ValueError, ValidationError, yaml.YAMLError):
            return None

    @staticmethod
    def _read(path: Path) -> TaskSpec:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"invalid task YAML: {path}")
        return TaskSpec.model_validate(data)

    @staticmethod
    def _write(path: Path, task: TaskSpec) -> None:
        path.write_text(yaml.safe_dump(task.model_dump(), sort_keys=False), encoding="utf-8")
