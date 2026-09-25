from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from causal_mind import cli_research
from causal_mind.orchestrator.coordinator import run_coordinator_once
from causal_mind.orchestrator.queue import TaskQueue
from causal_mind.orchestrator.qwen_client import QwenClient
from causal_mind.orchestrator.review import (
    drain_review_records,
    pending_review_records,
    write_review_batch,
    write_structured_reviews,
)
from causal_mind.orchestrator.status import collect_research_status


def _repo_root() -> Path:
    return Path(os.environ.get("CM_REPO_ROOT", Path.cwd())).resolve()


def _queue_root(root: Path) -> Path:
    return Path(os.environ.get("CM_QUEUE_ROOT", root / "orchestration" / "tasks"))


def _report_root(root: Path) -> Path:
    return Path(os.environ.get("CM_REPORT_ROOT", root / "reports"))


def _status(args: argparse.Namespace) -> int:
    root = _repo_root()
    status = collect_research_status(root, _queue_root(root))
    print(f"gpu:   {status.gpu_status}")
    print(f"qwen:  {status.qwen_status}")
    print(f"supervisors running: {status.healthy_supervisors}/{len(status.supervisors)}")
    for supervisor in status.supervisors:
        marker = "RUNNING" if supervisor.running else "stopped"
        print(f"  {supervisor.worker:<12} {marker}")
    print(f"active workers: {', '.join(status.active_workers) or '(none)'}")
    print(f"task counts: {status.task_counts}")
    return 0


def _task(args: argparse.Namespace) -> int:
    root = _repo_root()
    queue = TaskQueue(_queue_root(root))
    if args.action == "list":
        for task in queue.list_tasks():
            worker = task.assigned_worker or "-"
            print(f"{task.state:<8} {task.id:<16} worker={worker:<12} {task.title}")
        return 0
    if args.action == "claim":
        task = queue.claim_next(args.worker)
        if task is None:
            print("nothing to claim")
            return 1
        print(f"claimed {task.id} by {args.worker}")
        return 0
    if args.action in {"review", "done", "blocked", "killed", "queue"}:
        queue.transition(args.task_id, args.action)
        print(f"{args.task_id} -> {args.action}")
        return 0
    raise ValueError(f"unknown task action: {args.action}")


def _agent(args: argparse.Namespace) -> int:
    from causal_mind.agent.loop import AgentConfig, QwenToolLoopAgent
    from causal_mind.agent.prompts import system_prompt_for
    from causal_mind.agent.report import repo_file_context, task_prompt_for, write_agent_report

    root = _repo_root()
    worker = args.worker
    workdir = Path(os.environ.get("CM_WORKDIR", root))
    queue = TaskQueue(_queue_root(root))
    report_root = _report_root(root)

    max_tasks = args.max_tasks if args.action == "loop" else 1
    done = 0
    while max_tasks is None or done < max_tasks:
        task = queue.claim_next(worker)
        if task is None:
            print(f"{worker}: idle (queue empty or dependencies unsatisfied)")
            break
        config = AgentConfig(
            max_cycles=int(os.environ.get("CM_AGENT_MAX_CYCLES", "40")),
            request_timeout=int(os.environ.get("CM_AGENT_TIMEOUT", "300")),
        )
        agent = QwenToolLoopAgent(
            worker=worker,
            workdir=workdir,
            config=config,
            system_prompt=system_prompt_for(worker, repo_file_context(workdir)),
        )
        result = agent.run(task_prompt_for(task, repo_file_context(workdir)), task_id=task.id)
        path = write_agent_report(report_root, worker, task.id, result)
        print(
            f"{worker}: {task.id} stop={result.stop_reason} decision={result.decision} "
            f"cycles={result.cycles} duration={result.duration_s}s report={path}"
        )
        if result.stop_reason in {"endpoint_error", "repeated_command", "no_progress"}:
            queue.transition(task.id, "queue")
            print(f"{worker}: returned {task.id} to queue ({result.stop_reason})")
            break
        queue.transition(task.id, "review")
        done += 1
    return 0


def _coordinator(args: argparse.Namespace) -> int:
    root = _repo_root()
    result = run_coordinator_once(root, dry_run=args.dry_run)
    print(
        f"coordinator: state={result.state} tasks_created={result.tasks_created} "
        f"report={result.report_path}"
    )
    return 0


def _review(args: argparse.Namespace) -> int:
    root = _repo_root()
    queue_root = _queue_root(root)
    report_root = _report_root(root)
    records = pending_review_records(queue_root, root)
    if not records:
        print("nothing in review")
        return 0
    if args.action == "list":
        for record in records:
            print(f"{record.task_id:<16} {record.worker or '-':<12} {record.decision}")
        return 0
    review_dir = report_root / "reviews"
    write_structured_reviews(records, review_dir)
    write_review_batch(records, report_root / "reviews" / "latest_batch.md")
    drain_review_records(queue_root, records)
    print(f"drained {len(records)} review records")
    return 0


def _qwen(args: argparse.Namespace) -> int:
    client = QwenClient()
    if client.health():
        print(f"qwen healthy: {client.model} @ {client.base_url}")
        return 0
    print(f"qwen unreachable: {client.base_url}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cm", description="Causal Mind operations CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="research status").set_defaults(func=_status)

    task_parser = sub.add_parser("task", help="task queue operations")
    task_sub = task_parser.add_subparsers(dest="action", required=True)
    task_sub.add_parser("list")
    claim = task_sub.add_parser("claim")
    claim.add_argument("worker")
    for action in ("review", "done", "blocked", "killed", "queue"):
        p = task_sub.add_parser(action)
        p.add_argument("task_id")
    task_parser.set_defaults(func=_task)

    agent_parser = sub.add_parser("agent", help="run an agent worker")
    agent_sub = agent_parser.add_subparsers(dest="action", required=True)
    for action in ("once", "loop"):
        p = agent_sub.add_parser(action)
        p.add_argument("worker")
        p.add_argument("--max-tasks", type=int, default=None)
    agent_parser.set_defaults(func=_agent)

    coord_parser = sub.add_parser("coordinator", help="run a coordinator planning cycle")
    coord_sub = coord_parser.add_subparsers(dest="action", required=True)
    coord_run = coord_sub.add_parser("run")
    coord_run.add_argument("--dry-run", action="store_true")
    coord_parser.set_defaults(func=_coordinator)

    review_parser = sub.add_parser("review", help="review queue operations")
    review_sub = review_parser.add_subparsers(dest="action", required=True)
    review_sub.add_parser("list")
    review_sub.add_parser("drain")
    review_parser.set_defaults(func=_review)

    sub.add_parser("qwen", help="Qwen endpoint health").set_defaults(func=_qwen)

    # Research-facing commands (validate/doctor/claims/artifacts/security/demo/reproduce)
    cli_research.register(sub)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
