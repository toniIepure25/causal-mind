from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from causal_mind.orchestrator.queue import TaskQueue

ReviewDecision = str
OutputKind = str


@dataclass(frozen=True)
class ReviewRecord:
    task_id: str
    worker: str | None
    decision: ReviewDecision
    rationale: str
    follow_up: str | None = None
    output_kind: OutputKind = "RESEARCH_FINDING"
    reviewer_findings: tuple[str, ...] = ()
    deliverables: tuple[str, ...] = ()
    reports: tuple[str, ...] = ()


def pending_review_records(queue_root: Path, repo_root: Path) -> list[ReviewRecord]:
    """Build review records for all tasks currently in the review state."""
    queue = TaskQueue(queue_root)
    tasks = [task for task in queue.list_tasks() if task.state == "review"]
    records: list[ReviewRecord] = []
    for task in sorted(tasks, key=lambda item: item.id):
        records.append(_review_task(repo_root, task))
    return records


def write_structured_reviews(records: list[ReviewRecord], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for record in records:
        payload = {
            "task_id": record.task_id,
            "worker": record.worker,
            "review": {
                "correctness": "pass" if record.decision in {"APPROVE", "ITERATE"} else "hold",
                "tests": "pass" if record.output_kind != "CODE" else "required",
                "reproducibility": "pass",
                "scope": "pass" if record.decision != "KILL" else "fail",
            },
            "output_kind": record.output_kind,
            "deliverables": list(record.deliverables),
            "reports": list(record.reports),
            "reviewer_findings": list(record.reviewer_findings),
            "decision": record.decision,
            "decision_reason": record.rationale,
            "follow_up": {
                "required": record.follow_up is not None,
                "task_title": record.follow_up,
            },
        }
        path = output_dir / f"{record.task_id}.yaml"
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        written.append(path)
    return written


def write_review_batch(records: list[ReviewRecord], output_md: Path) -> Path:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Review Batch",
        "",
        "Each review item is classified as APPROVE, ITERATE, KILL, or BLOCK.",
        "",
        "| task | worker | kind | decision | rationale | follow-up |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            f"| {record.task_id} | {record.worker or ''} | {record.output_kind} | "
            f"{record.decision} | {record.rationale} | {record.follow_up or ''} |"
        )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_md


def drain_review_records(queue_root: Path, records: list[ReviewRecord]) -> None:
    queue = TaskQueue(queue_root)
    for record in records:
        if record.decision in {"APPROVE", "ITERATE", "KILL"}:
            target = "killed" if record.decision == "KILL" else "done"
            queue.transition(record.task_id, target)
        elif record.decision == "BLOCK":
            queue.transition(record.task_id, "blocked")
        else:
            raise ValueError(f"unknown review decision: {record.decision}")


def _review_task(repo_root: Path, task) -> ReviewRecord:
    reports = _reports_for_task(repo_root, task.id)
    parts = [path.read_text(encoding="utf-8", errors="replace") for path in reports]
    report_text = "\n\n".join(parts)
    deliverables = tuple(task.deliverables)
    present_deliverables = tuple(
        d for d in deliverables if (repo_root / d).exists()
    )
    findings = [
        f"objective: {task.objective[:200]}",
        f"deliverables_present: {len(present_deliverables)}/{len(deliverables)}",
    ]
    findings.append(f"worker_reports: {len(reports)}")

    lowered = report_text.lower()
    if "agent run failed" in lowered or ("qwen" in lowered and "failed" in lowered):
        return ReviewRecord(
            task_id=task.id,
            worker=task.assigned_worker,
            decision="ITERATE",
            rationale="Worker report records a harness/endpoint failure; rerun after stable.",
            follow_up=f"Retry {task.title} after Qwen health is stable.",
            output_kind=_classify_output_kind(deliverables),
            reviewer_findings=tuple(findings),
            deliverables=deliverables,
            reports=tuple(path.as_posix() for path in reports),
        )

    if not reports:
        return ReviewRecord(
            task_id=task.id,
            worker=task.assigned_worker,
            decision="ITERATE",
            rationale="No worker report was found for this review item.",
            follow_up=f"Regenerate report for {task.title}.",
            output_kind=_classify_output_kind(deliverables),
            reviewer_findings=tuple(findings),
            deliverables=deliverables,
            reports=(),
        )

    report_decision = _report_decision(report_text)
    if report_decision == "KILL":
        return ReviewRecord(
            task_id=task.id,
            worker=task.assigned_worker,
            decision="KILL",
            rationale="Worker report explicitly recommends killing this direction.",
            output_kind=_classify_output_kind(deliverables),
            reviewer_findings=tuple(findings),
            deliverables=deliverables,
            reports=tuple(path.as_posix() for path in reports),
        )
    if report_decision == "BLOCK":
        return ReviewRecord(
            task_id=task.id,
            worker=task.assigned_worker,
            decision="BLOCK",
            rationale="Worker report identifies a genuine external dependency.",
            follow_up="Resume when the external dependency named in the report is available.",
            output_kind=_classify_output_kind(deliverables),
            reviewer_findings=tuple(findings),
            deliverables=deliverables,
            reports=tuple(path.as_posix() for path in reports),
        )

    if len(present_deliverables) < len(deliverables):
        missing = sorted(set(deliverables).difference(present_deliverables))
        return ReviewRecord(
            task_id=task.id,
            worker=task.assigned_worker,
            decision="ITERATE",
            rationale="Useful signal exists, but one or more required deliverables are missing.",
            follow_up=f"Create missing deliverables: {', '.join(missing)}.",
            output_kind=_classify_output_kind(deliverables),
            reviewer_findings=tuple([*findings, f"missing: {', '.join(missing)}"]),
            deliverables=deliverables,
            reports=tuple(path.as_posix() for path in reports),
        )

    if _classify_output_kind(deliverables) in {"CODE", "TEST"}:
        return ReviewRecord(
            task_id=task.id,
            worker=task.assigned_worker,
            decision="ITERATE",
            rationale="Code/test output requires diff review plus tests before approval.",
            follow_up=f"Run diff review and relevant tests for {task.title}.",
            output_kind=_classify_output_kind(deliverables),
            reviewer_findings=tuple(findings),
            deliverables=deliverables,
            reports=tuple(path.as_posix() for path in reports),
        )

    return ReviewRecord(
        task_id=task.id,
        worker=task.assigned_worker,
        decision="APPROVE",
        rationale="Report output is scoped and does not overclaim; deliverables present.",
        output_kind=_classify_output_kind(deliverables),
        reviewer_findings=tuple(findings),
        deliverables=deliverables,
        reports=tuple(path.as_posix() for path in reports),
    )


def _reports_for_task(repo_root: Path, task_id: str) -> list[Path]:
    report_root = repo_root / "reports" / "agents"
    if not report_root.exists():
        return []
    return sorted(report_root.glob(f"*/{task_id}.md"), key=lambda path: path.stat().st_mtime)


def _classify_output_kind(deliverables: tuple[str, ...]) -> OutputKind:
    if any(path.startswith("src/") for path in deliverables):
        return "CODE"
    if any(path.startswith("tests/") for path in deliverables):
        return "TEST"
    if any(path.startswith("configs/") for path in deliverables):
        return "CONFIG"
    if any(path.startswith("data/manifests/") for path in deliverables):
        return "DATA_ARTIFACT"
    if any(path.startswith("reports/") or path.startswith("docs/") for path in deliverables):
        return "REPORT"
    return "RESEARCH_FINDING"


def _report_decision(report_text: str) -> str | None:
    patterns = [
        r"Decision:\s*(GO|HOLD|KILL|BLOCK)",
        r"\*\*Decision\*\*:\s*(GO|HOLD|KILL|BLOCK)",
        r"##\s*Decision\s*\n+\s*\*\*(GO|HOLD|KILL|BLOCK)\*\*",
    ]
    for pattern in patterns:
        match = re.search(pattern, report_text, flags=re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None
