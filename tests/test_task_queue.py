from __future__ import annotations

import threading
from pathlib import Path

import pytest
import yaml

from causal_mind.orchestrator.models import TaskSpec
from causal_mind.orchestrator.queue import TaskQueue


def make_task(task_id: str, **kwargs) -> TaskSpec:
    base = {"id": task_id, "title": f"title {task_id}", "objective": "do the thing"}
    base.update(kwargs)
    return TaskSpec(**base)


def write_task(queue: TaskQueue, task: TaskSpec, state: str = "queue") -> None:
    path = queue.root / state / f"{task.id}.yaml"
    path.write_text(yaml.safe_dump(task.model_dump()), encoding="utf-8")


@pytest.fixture()
def queue(tmp_path: Path) -> TaskQueue:
    return TaskQueue(tmp_path / "tasks")


def test_register_and_list(queue: TaskQueue) -> None:
    scratch = queue.root / "scratch.yaml"
    scratch.write_text(yaml.safe_dump(make_task("T1").model_dump()), encoding="utf-8")
    task = queue.register(scratch)
    assert task.state == "queue"
    listed = queue.list_tasks()
    assert [t.id for t in listed] == ["T1"]


def test_claim_moves_to_running(queue: TaskQueue) -> None:
    write_task(queue, make_task("T1"))
    task = queue.claim_next("worker-a")
    assert task is not None
    assert task.assigned_worker == "worker-a"
    assert (queue.root / "running" / "T1.yaml").exists()
    assert not (queue.root / "queue" / "T1.yaml").exists()


def test_claim_respects_assignment(queue: TaskQueue) -> None:
    write_task(queue, make_task("T1", assigned_worker="worker-a"))
    assert queue.claim_next("worker-b") is None
    assert queue.claim_next("worker-a") is not None


def test_claim_skips_unsatisfied_dependencies(queue: TaskQueue) -> None:
    write_task(queue, make_task("T1"))
    write_task(queue, make_task("T2", dependencies=["T1"]))
    first = queue.claim_next("w")
    assert first is not None and first.id == "T1"
    assert queue.claim_next("w") is None  # T2 blocked until T1 done
    queue.transition("T1", "done")
    second = queue.claim_next("w")
    assert second is not None and second.id == "T2"


def test_transitions(queue: TaskQueue) -> None:
    write_task(queue, make_task("T1"))
    queue.claim_next("w")
    queue.transition("T1", "review")
    assert (queue.root / "review" / "T1.yaml").exists()
    queue.transition("T1", "done")
    assert (queue.root / "done" / "T1.yaml").exists()
    assert "T1" in queue.done_ids()


def test_concurrent_claims_single_winner(queue: TaskQueue) -> None:
    write_task(queue, make_task("T1"))
    results: list = []
    barrier = threading.Barrier(4)

    def worker(name: str) -> None:
        barrier.wait()
        results.append(TaskQueue(queue.root).claim_next(name))

    threads = [threading.Thread(target=worker, args=(f"w{i}",)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    claimed = [r for r in results if r is not None]
    assert len(claimed) == 1
    assert (queue.root / "running" / "T1.yaml").exists()


def test_corrupt_yaml_ignored(queue: TaskQueue) -> None:
    (queue.root / "queue" / "bad.yaml").write_text("::: not yaml :::", encoding="utf-8")
    write_task(queue, make_task("T1"))
    tasks = queue.list_tasks()
    assert [t.id for t in tasks] == ["T1"]
