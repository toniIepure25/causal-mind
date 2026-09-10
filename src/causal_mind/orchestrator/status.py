from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from causal_mind.monitoring.gpu import collect_system_snapshot
from causal_mind.orchestrator.queue import TaskQueue
from causal_mind.orchestrator.workers import WORKERS


@dataclass(frozen=True)
class SupervisorState:
    worker: str
    running: bool
    pid: int | None
    log_path: Path


@dataclass(frozen=True)
class ResearchStatus:
    supervisors: list[SupervisorState]
    active_workers: list[str]
    idle_workers: list[str]
    task_counts: dict[str, int]
    gpu_status: str
    qwen_status: str

    @property
    def healthy_supervisors(self) -> int:
        return sum(1 for supervisor in self.supervisors if supervisor.running)

    @property
    def active_research_work(self) -> bool:
        return bool(
            self.active_workers
            or self.task_counts.get("queue", 0)
            or self.task_counts.get("running", 0)
            or self.task_counts.get("review", 0)
        )


def collect_research_status(root: Path, queue_root: Path) -> ResearchStatus:
    queue = TaskQueue(queue_root)
    tasks = queue.list_tasks()
    counts = queue.count_by_state()
    active_workers = sorted(
        {
            task.assigned_worker
            for task in tasks
            if task.state == "running" and task.assigned_worker is not None
        }
    )
    supervisors = [supervisor_state(root, worker) for worker in WORKERS]
    healthy_workers = {supervisor.worker for supervisor in supervisors if supervisor.running}
    idle_workers = sorted(healthy_workers.difference(active_workers))
    snapshot = collect_system_snapshot(root)
    return ResearchStatus(
        supervisors=supervisors,
        active_workers=active_workers,
        idle_workers=idle_workers,
        task_counts=counts,
        gpu_status=snapshot.gpu_status,
        qwen_status=snapshot.qwen_status,
    )


def supervisor_state(root: Path, worker: str) -> SupervisorState:
    run_dir = root / "orchestration" / "logs"
    pid_path = run_dir / "pids" / f"{worker}.pid"
    pid = _read_pid(pid_path)
    return SupervisorState(
        worker=worker,
        running=_pid_running(pid),
        pid=pid,
        log_path=run_dir / "supervisors" / f"{worker}.log",
    )


def _read_pid(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError, OSError):
        return None


def _pid_running(pid: int | None) -> bool:
    if pid is None:
        return False
    return (Path("/proc") / str(pid)).exists()
