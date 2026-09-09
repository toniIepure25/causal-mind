from __future__ import annotations

from pathlib import Path

import yaml

from causal_mind.orchestrator.models import TaskSpec
from causal_mind.orchestrator.queue import TaskQueue
from causal_mind.orchestrator.review import (
    drain_review_records,
    pending_review_records,
    write_review_batch,
    write_structured_reviews,
)


def make_task(task_id: str, **kwargs) -> TaskSpec:
    base = {"id": task_id, "title": f"title {task_id}", "objective": "do the thing"}
    base.update(kwargs)
    return TaskSpec(**base)


def test_no_review_records(tmp_path: Path) -> None:
    queue = TaskQueue(tmp_path / "tasks")
    records = pending_review_records(tmp_path / "tasks", tmp_path)
    assert records == []


def test_review_approve_with_report(tmp_path: Path) -> None:
    queue = TaskQueue(tmp_path / "tasks")
    (tmp_path / "tasks" / "T1.yaml").write_text(
        yaml.safe_dump(make_task("T1", deliverables=["reports/x.md"]).model_dump()),
        encoding="utf-8",
    )
    queue.claim_next("w")
    queue.transition("T1", "review")
    (tmp_path / "reports" / "x.md").write_text("result\n", encoding="utf-8")
    report_dir = tmp_path / "reports" / "agents" / "w"
    report_dir.mkdir(parents=True)
    (report_dir / "T1.md").write_text("## 1. Decision\nGO\n", encoding="utf-8")

    records = pending_review_records(tmp_path / "tasks", tmp_path)
    assert len(records) == 1
    record = records[0]
    assert record.decision == "APPROVE"

    out = tmp_path / "reviews"
    write_structured_reviews(records, out)
    write_review_batch(records, out / "batch.md")
    drain_review_records(tmp_path / "tasks", records)
    assert (tmp_path / "tasks" / "done" / "T1.yaml").exists()


def test_review_kill(tmp_path: Path) -> None:
    queue = TaskQueue(tmp_path / "tasks")
    (tmp_path / "tasks" / "T2.yaml").write_text(
        yaml.safe_dump(make_task("T2").model_dump()), encoding="utf-8"
    )
    queue.claim_next("w")
    queue.transition("T2", "review")
    report_dir = tmp_path / "reports" / "agents" / "w"
    report_dir.mkdir(parents=True)
    (report_dir / "T2.md").write_text("Decision: KILL\n", encoding="utf-8")

    records = pending_review_records(tmp_path / "tasks", tmp_path)
    assert records[0].decision == "KILL"
    drain_review_records(tmp_path / "tasks", records)
    assert (tmp_path / "tasks" / "killed" / "T2.yaml").exists()


def test_review_missing_deliverable_iterates(tmp_path: Path) -> None:
    queue = TaskQueue(tmp_path / "tasks")
    (tmp_path / "tasks" / "T3.yaml").write_text(
        yaml.safe_dump(make_task("T3", deliverables=["reports/missing.md"]).model_dump()),
        encoding="utf-8",
    )
    queue.claim_next("w")
    queue.transition("T3", "review")
    report_dir = tmp_path / "reports" / "agents" / "w"
    report_dir.mkdir(parents=True)
    (report_dir / "T3.md").write_text("Decision: GO\n", encoding="utf-8")

    records = pending_review_records(tmp_path / "tasks", tmp_path)
    assert records[0].decision == "ITERATE"
    assert "missing" in records[0].follow_up or "missing" in records[0].rationale
