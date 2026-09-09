from __future__ import annotations

from pathlib import Path

from causal_mind.agent.loop import AgentRunResult


def repo_file_context(root: Path, limit: int = 150) -> str:
    skip_dirs = {
        ".git",
        ".venv",
        ".uv-cache",
        ".home",
        ".opencode",
        ".runai-cli",
        ".runai-proxy",
        ".caddy",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "data",
    }
    files: list[str] = []
    for path in root.rglob("*"):
        if len(files) >= limit:
            break
        if any(part in skip_dirs for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            files.append(path.relative_to(root).as_posix())
    return "\n".join(files) if files else "(empty)"


def task_prompt_for(task, repo_context: str) -> str:
    return f"""Execute this task in your worktree.

Task:
- id: {task.id}
- title: {task.title}
- hypothesis: {task.hypothesis or '(none)'}
- objective: {task.objective}
- allowed paths: {task.allowed_paths}
- forbidden paths: {task.forbidden_paths}
- required tests: {task.required_tests}
- success criteria: {task.success_criteria}
- failure criteria: {task.failure_criteria}
- deliverables: {task.deliverables}

Repository files:
{repo_context}

Work autonomously: inspect, implement, test (run pytest/ruff where relevant), and write
your deliverables. Keep changes minimal and within allowed paths. When finished, end
with your Decision line.
""".strip()


def write_agent_report(
    report_root: Path, worker: str, task_id: str, result: AgentRunResult
) -> Path:
    report_dir = report_root / "agents" / worker
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{task_id}.md"
    path.write_text(result.report_text, encoding="utf-8")
    return path
