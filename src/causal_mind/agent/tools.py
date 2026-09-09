from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

MAX_OUTPUT_CHARS = 12000
DEFAULT_TIMEOUT = 300

# Commands/patterns that must never run inside an agent tool loop.
DENY_PATTERNS: tuple[str, ...] = (
    r"git\s+push",
    r"git\s+reset\s+--hard",
    r"git\s+clean",
    r"git\s+remote\s+add",
    r"kubectl",
    r"ssh\s",
    r"scp\s",
    r"sudo\s",
    r"rm\s+(-[a-z]*\s+)*-[a-z]*r[a-z]*\s+(/|~|\$HOME)",
    r"\.runai",
    r"\.runai-proxy",
    r"\.ssh",
    r"id_ed25519",
    r"authorized_keys",
    r"kubeconfig",
    r"\.env\b",
    r"curl.*\|\s*(ba)?sh",
    r"wget.*\|\s*(ba)?sh",
    r":\(\)\s*\{",  # fork bomb
    r"mkfs",
    r"dd\s+if=",
    r"chmod\s+-R",
    r"shutdown",
    r"reboot",
)

_DENY_RE = [re.compile(p) for p in DENY_PATTERNS]


class ToolError(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    output: str
    changed_files: tuple[str, ...] = ()


def _truncate(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[truncated {len(text) - limit} chars]"


def _resolve_within(workdir: Path, raw: str) -> Path:
    workdir = workdir.resolve()
    candidate = (workdir / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
    if workdir != candidate and workdir not in candidate.parents:
        raise ToolError(f"path escapes workdir: {raw}")
    return candidate


def _check_command(command: str, workdir: Path) -> None:
    for pattern in _DENY_RE:
        if pattern.search(command):
            raise ToolError(f"command denied by policy: {command[:120]}")
    # Absolute paths outside the workdir in rm/mv/cp targets are denied.
    if re.search(r"\b(rm|mv|cp)\b", command):
        for match in re.finditer(r"(/[^\s'\"]+)", command):
            target = match.group(1)
            if target.startswith(workdir.resolve().as_posix()):
                continue
            if target in {"/dev/null", "/dev/stdout", "/dev/stderr"}:
                continue
            if target.startswith(("/tmp/", "/var/tmp/")):
                continue
            raise ToolError(f"command touches path outside workdir: {target}")


def run_bash(command: str, workdir: Path, timeout: int = DEFAULT_TIMEOUT) -> ToolResult:
    _check_command(command, workdir)
    env_path = (
        "/home/jovyan/work/.local/bin:"
        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    )
    import os

    env = os.environ.copy()
    env["PATH"] = env_path
    try:
        result = subprocess.run(
            ["bash", "-lc", command],
            cwd=workdir,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ToolResult(ok=False, output=f"command timed out after {timeout}s: {command[:120]}")
    output = _truncate(result.stdout)
    return ToolResult(ok=result.returncode == 0, output=f"exit={result.returncode}\n{output}")


def run_read(path: str, workdir: Path, max_chars: int = 20000) -> ToolResult:
    target = _resolve_within(workdir, path)
    if not target.is_file():
        return ToolResult(ok=False, output=f"not a file: {path}")
    text = target.read_text(encoding="utf-8", errors="replace")
    return ToolResult(ok=True, output=_truncate(text, max_chars))


def run_write(path: str, content: str, workdir: Path) -> ToolResult:
    target = _resolve_within(workdir, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return ToolResult(ok=True, output=f"wrote {len(content)} chars to {path}", changed_files=(path,))


def run_edit(path: str, old_string: str, new_string: str, workdir: Path) -> ToolResult:
    target = _resolve_within(workdir, path)
    if not target.is_file():
        return ToolResult(ok=False, output=f"not a file: {path}")
    text = target.read_text(encoding="utf-8")
    count = text.count(old_string)
    if count == 0:
        return ToolResult(ok=False, output=f"old_string not found in {path}")
    if count > 1:
        return ToolResult(ok=False, output=f"old_string found {count} times in {path}; be more specific")
    target.write_text(text.replace(old_string, new_string, 1), encoding="utf-8")
    return ToolResult(ok=True, output=f"edited {path}", changed_files=(path,))


def run_grep(pattern: str, workdir: Path, path: str = ".", max_results: int = 50) -> ToolResult:
    base = _resolve_within(workdir, path)
    regex = re.compile(pattern)
    hits: list[str] = []
    targets = [base] if base.is_file() else sorted(p for p in base.rglob("*") if p.is_file())
    for target in targets:
        if any(part in {".git", ".venv", "__pycache__", ".uv-cache"} for part in target.parts):
            continue
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if regex.search(line):
                rel = target.relative_to(workdir).as_posix()
                hits.append(f"{rel}:{lineno}: {line[:200]}")
                if len(hits) >= max_results:
                    return ToolResult(ok=True, output="\n".join(hits))
    return ToolResult(ok=True, output="\n".join(hits) if hits else "(no matches)")


def run_glob(pattern: str, workdir: Path, max_results: int = 100) -> ToolResult:
    base = workdir.resolve()
    matches = sorted(
        p.relative_to(base).as_posix()
        for p in base.glob(pattern)
        if not any(part in {".git", ".venv", "__pycache__", ".uv-cache"} for part in p.parts)
    )
    if len(matches) > max_results:
        matches = matches[:max_results]
    return ToolResult(ok=True, output="\n".join(matches) if matches else "(no matches)")


TOOLS: dict[str, dict[str, object]] = {
    "bash": {
        "description": "Run a shell command in the project workdir. Output is truncated.",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
            "additionalProperties": False,
        },
    },
    "read": {
        "description": "Read a text file (path relative to the project workdir).",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    "write": {
        "description": "Write a text file (path relative to the project workdir). Overwrites.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    "edit": {
        "description": "Replace an exact unique string in a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_string": {"type": "string"},
                "new_string": {"type": "string"},
            },
            "required": ["path", "old_string", "new_string"],
            "additionalProperties": False,
        },
    },
    "grep": {
        "description": "Regex-search files under a path (relative to the workdir).",
        "parameters": {
            "type": "object",
            "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}},
            "required": ["pattern"],
            "additionalProperties": False,
        },
    },
    "glob": {
        "description": "Glob file paths (relative to the workdir).",
        "parameters": {
            "type": "object",
            "properties": {"pattern": {"type": "string"}},
            "required": ["pattern"],
            "additionalProperties": False,
        },
    },
}


def tool_schemas() -> list[dict[str, object]]:
    return [
        {"type": "function", "function": {"name": name, **spec}} for name, spec in TOOLS.items()
    ]


def execute_tool(name: str, args: dict[str, object], workdir: Path) -> ToolResult:
    try:
        if name == "bash":
            return run_bash(str(args.get("command", "")), workdir)
        if name == "read":
            return run_read(str(args.get("path", "")), workdir)
        if name == "write":
            return run_write(str(args.get("path", "")), str(args.get("content", "")), workdir)
        if name == "edit":
            return run_edit(
                str(args.get("path", "")),
                str(args.get("old_string", "")),
                str(args.get("new_string", "")),
                workdir,
            )
        if name == "grep":
            return run_grep(str(args.get("pattern", "")), workdir, str(args.get("path", ".")))
        if name == "glob":
            return run_glob(str(args.get("pattern", "")), workdir)
        return ToolResult(ok=False, output=f"unknown tool: {name}")
    except ToolError as exc:
        return ToolResult(ok=False, output=str(exc))
    except (OSError, re.error) as exc:
        return ToolResult(ok=False, output=f"tool error: {exc}")


def args_hash(name: str, args: dict[str, object]) -> str:
    return f"{name}:{json.dumps(args, sort_keys=True, ensure_ascii=False)}"
