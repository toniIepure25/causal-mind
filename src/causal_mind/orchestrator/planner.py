from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml

from causal_mind.orchestrator.models import TaskSpec
from causal_mind.orchestrator.qwen_client import QwenClient

ALLOWED_WORKERS = ("researcher", "data", "forecasting", "causal", "reviewer")
REQUIRED_FORBIDDEN = (".runai", ".runai-proxy", ".ssh", ".env")
MAX_TASKS = 3

MILESTONES = (
    "CM0_EPISTEMIC_SEAL",
    "CM1_DATA_AUDIT",
    "CM2_THOUGHT_STATE_V0",
    "CM3_NEXT_BASELINES",
    "CM4_MULTI_STEP_FUTURES",
    "CM5_NEURAL_INCREMENTAL",
    "CM6_BRAIN_REPRESENTATION",
    "CM7_WORLD_MODEL",
    "CM8_CAUSAL_GENEALOGY",
    "CM9_COUNTERFACTUAL",
    "CM10_EEG_EXTENSION",
    "CM11_BREAK_CHAIN_DESIGN",
    "CM12_ORACLE_DESIGN",
    "CM13_RECURSIVE_ORACLE",
)

# Every generated task must answer these four questions.
REQUIRED_ANSWERS = ("milestone", "new_evidence", "decision_impact", "why_not_idle")

STATE_FILE = Path("reports") / "research" / "planner_state.json"


def plan_next_tasks(
    repo_root: Path,
    existing_ids: set[str],
    synthesis: str | None = None,
) -> list[TaskSpec]:
    """Plan new tasks only when fresh evidence justifies them."""
    evidence_hash = _evidence_hash(repo_root)
    if _evidence_unchanged(repo_root, evidence_hash):
        return []

    context = gather_context(repo_root)
    prompt = _build_prompt(context, synthesis, existing_ids)
    client = QwenClient()
    response = client.complete(prompt, max_tokens=3000)
    tasks = _parse_tasks(response, existing_ids)
    _record_planning(repo_root, evidence_hash)
    return tasks[:MAX_TASKS]


def _evidence_hash(repo_root: Path) -> str:
    entries: list[str] = []
    reports_dir = repo_root / "reports"
    if reports_dir.exists():
        for path in sorted(reports_dir.rglob("*.md")):
            try:
                entries.append(f"{path.name}:{int(path.stat().st_mtime)}")
            except OSError:
                continue
    head = _run(repo_root, ["git", "rev-parse", "HEAD"])
    return hashlib.sha256(("\n".join(entries) + "\n" + head).encode("utf-8")).hexdigest()


def _state_path(repo_root: Path) -> Path:
    return repo_root / STATE_FILE


def _evidence_unchanged(repo_root: Path, evidence_hash: str) -> bool:
    state_path = _state_path(repo_root)
    if not state_path.exists():
        return False
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return state.get("evidence_hash") == evidence_hash


def _record_planning(repo_root: Path, evidence_hash: str) -> None:
    state_path = _state_path(repo_root)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"evidence_hash": evidence_hash}, indent=2), encoding="utf-8"
    )


def _recent_task_titles(repo_root: Path) -> str:
    tasks_dir = repo_root / "orchestration" / "tasks"
    titles: list[str] = []
    for state in ("done", "queue", "running", "review"):
        state_dir = tasks_dir / state
        if not state_dir.exists():
            continue
        for path in sorted(state_dir.glob("*.yaml")):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                title = data.get("title", path.stem)
                titles.append(f"{path.stem}: {title}")
            except Exception:
                continue
    return "\n".join(titles[-40:]) or "(none)"


def gather_context(repo_root: Path) -> str:
    git_log = _run(repo_root, ["git", "log", "--oneline", "-15"])
    modules = _list_modules(repo_root)
    reports = _recent_reports(repo_root)
    completed_titles = _recent_task_titles(repo_root)
    return (
        "Recent commits:\n"
        f"{git_log}\n\n"
        "Existing modules (src/causal_mind):\n"
        f"{modules}\n\n"
        "Recent reports:\n"
        f"{reports}\n\n"
        "Recently completed/active task titles (do NOT regenerate these):\n"
        f"{completed_titles}"
    )


def _build_prompt(context: str, synthesis: str | None, existing_ids: set[str]) -> str:
    done = ", ".join(sorted(existing_ids)) or "(none)"
    milestones = ", ".join(MILESTONES)
    synthesis_block = (
        synthesis.strip() if synthesis and synthesis.strip() else "(no synthesis available yet)"
    )
    return (
        "You are the autonomous research coordinator for the CAUSAL MIND lab: a causal\n"
        "world model for forecasting and redirecting human thought. Primary public data:\n"
        "OpenNeuro ds006067 (think-aloud spontaneous thought + fMRI). Compute: one A100.\n"
        "\n"
        "POLICY — be conservative. Do NOT manufacture work to keep workers busy.\n"
        "- Generate tasks ONLY if fresh evidence justifies them (a new result, a failed\n"
        "  experiment needing correction, a new dataset fact, an unresolved gate item).\n"
        "- If NONE of those exist, return an empty JSON array []. IDLE IS ACCEPTABLE.\n"
        "- Every task must advance exactly one milestone from: " + milestones + ".\n"
        "- Every task must answer all four questions (non-empty):\n"
        "  milestone: which milestone it advances\n"
        "  new_evidence: what new evidence will it produce\n"
        "  decision_impact: what decision could change because of the result\n"
        "  why_not_idle: why this is better than leaving the worker idle\n"
        "- Reject (do not emit) any task that cannot answer all four questions.\n"
        "\n"
        "HARD CONSTRAINTS for every task you generate:\n"
        "- Must respect the frozen validation protocol (subject-disjoint splits, no\n"
        "  peeking at the final holdout, claims registered at correct levels).\n"
        "- Must NOT read or write .runai, .runai-proxy, .ssh, .env, or any credential.\n"
        "- Must NOT fabricate results or inflate claim levels.\n"
        "- Must be a concrete, testable step with deliverables.\n"
        "- assigned_worker must be one of: "
        + ", ".join(ALLOWED_WORKERS)
        + ".\n"
        "- allowed_paths must be within src/, tests/, reports/, configs/, data/manifests/,\n"
        "  experiments/, docs/, orchestration/.\n"
        "\n"
        "LATEST LEAD SYNTHESIS:\n" + synthesis_block + "\n\n"
        "LAB STATE:\n" + context + "\n\n"
        "Already-completed or queued task IDs (do NOT repeat these):\n" + done + "\n\n"
        "Generate at most "
        f"{MAX_TASKS} NEW high-value tasks. Each must be DISTINCT from the recently\n"
        "completed task titles above and from the synthesis. Use a fresh loop prefix\n"
        "(e.g. LOOP1-001) for the ids.\n"
        "\n"
        "Return ONLY a JSON array of objects, each with exactly these keys:\n"
        "id, title, assigned_worker, objective, hypothesis, resource_class, expected_runtime, "
        "allowed_paths (array), forbidden_paths (array), success_criteria (array), "
        "failure_criteria (array), deliverables (array), milestone, new_evidence, "
        "decision_impact, why_not_idle.\n"
        "resource_class must be \"cpu\" or \"gpu-light\". expected_runtime like \"30m\".\n"
        "No markdown, no prose. If no fresh evidence justifies new work, return [] ."
    )


def _parse_tasks(response: str, existing_ids: set[str]) -> list[TaskSpec]:
    items = _extract_json_array(response)
    tasks: list[TaskSpec] = []
    seen: set[str] = set(existing_ids)
    for item in items:
        task = _to_task(item, seen)
        if task is not None:
            tasks.append(task)
            seen.add(task.id)
    return tasks


def _extract_json_array(text: str) -> list[dict[str, object]]:
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return []
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def _answer(item: dict[str, object], key: str) -> str:
    return str(item.get(key, "")).strip()


def _to_task(item: dict[str, object], seen: set[str]) -> TaskSpec | None:
    task_id = str(item.get("id", "")).strip()
    if not task_id or task_id in seen:
        return None
    title = str(item.get("title", "")).strip()
    objective = str(item.get("objective", "")).strip()
    worker = str(item.get("assigned_worker", "")).strip()
    if not title or not objective or worker not in ALLOWED_WORKERS:
        return None

    milestone = _answer(item, "milestone")
    new_evidence = _answer(item, "new_evidence")
    decision_impact = _answer(item, "decision_impact")
    why_not_idle = _answer(item, "why_not_idle")
    if milestone not in MILESTONES:
        return None
    if not new_evidence or not decision_impact or not why_not_idle:
        return None

    allowed_paths = [str(p) for p in item.get("allowed_paths", []) if str(p).strip()]
    if not allowed_paths:
        return None
    forbidden_paths = [str(p) for p in item.get("forbidden_paths", []) if str(p).strip()]
    for required in REQUIRED_FORBIDDEN:
        if required not in forbidden_paths:
            forbidden_paths.append(required)

    resource_class = str(item.get("resource_class", "cpu")).strip()
    if resource_class not in ("cpu", "gpu-light", "gpu-exclusive"):
        resource_class = "cpu"

    rationale = (
        f"[milestone] {milestone}\n"
        f"[new_evidence] {new_evidence}\n"
        f"[decision_impact] {decision_impact}\n"
        f"[why_not_idle] {why_not_idle}\n"
        f"{objective}"
    )
    return TaskSpec(
        id=task_id,
        title=title,
        owner="orchestrator",
        assigned_worker=worker,
        objective=rationale,
        hypothesis=str(item.get("hypothesis", "")).strip() or None,
        resource_class=resource_class,  # type: ignore[arg-type]
        expected_runtime=str(item.get("expected_runtime", "30m")).strip() or "30m",
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
        success_criteria=[str(s) for s in item.get("success_criteria", []) if str(s).strip()],
        failure_criteria=[str(k) for k in item.get("failure_criteria", []) if str(k).strip()],
        deliverables=[str(d) for d in item.get("deliverables", []) if str(d).strip()],
    )


def _run(repo_root: Path, command: list[str]) -> str:
    try:
        result = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "(unavailable)"


def _list_modules(repo_root: Path) -> str:
    root = repo_root / "src" / "causal_mind"
    if not root.exists():
        return "(none)"
    modules = sorted(
        str(path.relative_to(repo_root))
        for path in root.rglob("*.py")
        if path.name != "__init__.py"
    )
    return "\n".join(modules[:80]) or "(none)"


def _recent_reports(repo_root: Path) -> str:
    reports_dir = repo_root / "reports"
    if not reports_dir.exists():
        return "(none)"
    reports = sorted(
        (p for p in reports_dir.rglob("*.md") if "agents" not in p.parts),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )[:15]
    return "\n".join(p.name for p in reports) or "(none)"
