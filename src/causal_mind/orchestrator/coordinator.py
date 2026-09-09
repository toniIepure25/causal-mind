from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml

from causal_mind.orchestrator.planner import plan_next_tasks
from causal_mind.orchestrator.queue import TaskQueue

# Generate new work only while at most this many tasks are active.
DEFAULT_MAX_ACTIVE = 3
# Require a fresh synthesis after this many completed tasks.
SYNTHESIS_INTERVAL = 8

SYNTHESIS_PATH = Path("reports") / "research" / "synthesis_latest.md"
SYNTHESIS_STATE = Path("reports") / "research" / "synthesis_state.json"


@dataclass(frozen=True)
class CoordinatorRunResult:
    worker: str
    state: str
    tasks_created: int
    report_path: Path | None = None


def _utc_now() -> str:
    return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_coordinator_once(
    root: Path,
    *,
    max_active: int = DEFAULT_MAX_ACTIVE,
    dry_run: bool = False,
) -> CoordinatorRunResult:
    """Run one conservative coordinator planning cycle."""
    queue_root = Path(os.environ.get("CM_QUEUE_ROOT", root / "orchestration" / "tasks"))
    report_root = Path(os.environ.get("CM_REPORT_ROOT", root / "reports"))
    queue = TaskQueue(queue_root)
    counts = queue.count_by_state()
    active = counts.get("queue", 0) + counts.get("running", 0) + counts.get("review", 0)
    done = counts.get("done", 0)

    if active > max_active:
        return _write_idle_report(report_root, active, max_active, done, "queue_full")

    synthesis, is_due, done_at_synthesis = _synthesis_status(root, done)
    if is_due:
        return _write_synthesis_due_report(report_root, active, max_active, done, done_at_synthesis)

    existing = {task.id for task in queue.list_tasks()}
    tasks = [] if dry_run else plan_next_tasks(root, existing, synthesis=synthesis)

    created = 0
    created_ids: list[str] = []
    for task in tasks:
        if task.id in existing:
            continue
        path = queue_root / "queue" / f"{task.id}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(task.model_dump(), sort_keys=False), encoding="utf-8")
        created += 1
        created_ids.append(f"{task.id}: {task.title}")

    report_dir = report_root / "agents" / "orchestrator"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "latest.md"
    report = (
        f"# Coordinator Report\n\n"
        f"Generated: {_utc_now()}\n"
        f"Worker: orchestrator\n\n"
        f"Active depth before: {active} (max_active={max_active})\n"
        f"Done: {done}\n"
        f"Tasks created: {created}\n\n"
    )
    if created_ids:
        report += "New tasks:\n" + "\n".join(f"- {line}" for line in created_ids) + "\n"
    else:
        report += (
            "No new tasks generated (no fresh evidence, planner returned none, "
            "or dry run). IDLE IS ACCEPTABLE.\n"
        )
    report_path.write_text(report, encoding="utf-8")

    state = "planned" if created else "idle"
    return CoordinatorRunResult(
        worker="orchestrator", state=state, tasks_created=created, report_path=report_path
    )


def _synthesis_status(root: Path, done: int) -> tuple[str | None, bool, int]:
    synthesis_path = root / SYNTHESIS_PATH
    state_path = root / SYNTHESIS_STATE
    synthesis_text: str | None = None
    synthesis_mtime = 0
    if synthesis_path.exists():
        synthesis_text = synthesis_path.read_text(encoding="utf-8")
        synthesis_mtime = int(synthesis_path.stat().st_mtime)

    state: dict[str, object] = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            state = {}

    last_mtime = int(state.get("synthesis_mtime", 0))
    last_done = int(state.get("done_at_synthesis", 0))

    if synthesis_mtime > last_mtime:
        _write_synthesis_state(root, synthesis_mtime, done)
        return synthesis_text, False, done

    is_due = (done - last_done) >= SYNTHESIS_INTERVAL
    return synthesis_text, is_due, last_done


def _write_synthesis_state(root: Path, synthesis_mtime: int, done: int) -> None:
    state_path = root / SYNTHESIS_STATE
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"synthesis_mtime": synthesis_mtime, "done_at_synthesis": done}, indent=2),
        encoding="utf-8",
    )


def _write_idle_report(
    report_root: Path, active: int, max_active: int, done: int, reason: str
) -> CoordinatorRunResult:
    report_dir = report_root / "agents" / "orchestrator"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "latest.md"
    report = (
        f"# Coordinator Report\n\n"
        f"Generated: {_utc_now()}\n"
        f"Worker: orchestrator\n\n"
        f"Active depth: {active} (max_active={max_active})\n"
        f"Done: {done}\n"
        f"State: idle ({reason})\n\n"
        "Queue has enough active work; no new tasks generated.\n"
    )
    report_path.write_text(report, encoding="utf-8")
    return CoordinatorRunResult(
        worker="orchestrator", state="idle", tasks_created=0, report_path=report_path
    )


def _write_synthesis_due_report(
    report_root: Path, active: int, max_active: int, done: int, done_at_synthesis: int
) -> CoordinatorRunResult:
    report_dir = report_root / "agents" / "orchestrator"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "latest.md"
    report = (
        f"# Coordinator Report\n\n"
        f"Generated: {_utc_now()}\n"
        f"Worker: orchestrator\n\n"
        f"Active depth: {active} (max_active={max_active})\n"
        f"Done: {done} (was {done_at_synthesis} at last synthesis)\n"
        f"State: synthesis_due\n\n"
        f"A lead synthesis is required before generating a new branch "
        f"(+{done - done_at_synthesis} completed tasks since "
        f"{SYNTHESIS_PATH}). Update {SYNTHESIS_PATH} to resume planning.\n"
    )
    report_path.write_text(report, encoding="utf-8")
    return CoordinatorRunResult(
        worker="orchestrator", state="synthesis_due", tasks_created=0, report_path=report_path
    )
