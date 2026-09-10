from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from causal_mind.agent.tools import ToolResult, args_hash, execute_tool, tool_schemas
from causal_mind.orchestrator.qwen_client import QwenClient, QwenError


@dataclass
class AgentConfig:
    max_cycles: int = 40
    max_output_chars: int = 12000
    repeated_command_limit: int = 3
    no_progress_limit: int = 6
    context_budget_chars: int = 240000
    request_timeout: int = 300
    max_retries: int = 3
    temperature: float = 0.2
    max_tokens: int = 4096


@dataclass
class AgentRunResult:
    worker: str
    task_id: str | None
    stop_reason: str
    decision: str | None
    cycles: int
    commands_run: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    report_text: str = ""
    duration_s: float = 0.0
    error: str | None = None


def _utc_now() -> str:
    return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class QwenToolLoopAgent:
    """Bounded tool-loop agent on the shared Qwen endpoint.

    Guards: max cycles, repeated-command detection, no-progress detection, context
    budget, retry with backoff.
    """

    def __init__(
        self,
        worker: str,
        workdir: Path,
        *,
        client: QwenClient | None = None,
        config: AgentConfig | None = None,
        system_prompt: str,
    ) -> None:
        self.worker = worker
        self.workdir = workdir.resolve()
        self.client = client or QwenClient()
        self.config = config or AgentConfig()
        self.system_prompt = system_prompt

    def run(self, task_prompt: str, task_id: str | None = None) -> AgentRunResult:
        started = time.time()
        messages: list[dict[str, object]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task_prompt},
        ]
        recent_calls: list[str] = []
        seen_outputs: set[str] = set()
        files_changed: set[str] = set()
        commands_run: list[str] = []
        stop_reason = "max_cycles"
        final_content = ""
        error: str | None = None
        cycles = 0

        for _ in range(self.config.max_cycles):
            cycles += 1
            response = self._chat_with_retry(messages)
            if response is None:
                stop_reason = "endpoint_error"
                error = "Qwen endpoint failed after retries"
                break

            message = response["choices"][0]["message"]
            tool_calls = message.get("tool_calls") or []
            content = message.get("content") or ""

            if not tool_calls:
                if content.strip():
                    final_content = content
                    stop_reason = "completed"
                    break
                # Empty final message: nudge the model to continue.
                messages.append({"role": "assistant", "content": ""})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your last message was empty. Continue the task, or end with "
                            "your final answer including the Decision line."
                        ),
                    }
                )
                continue

            assistant_entry: dict[str, object] = {"role": "assistant", "content": content}
            if tool_calls:
                assistant_entry["tool_calls"] = tool_calls
            messages.append(assistant_entry)

            progress_this_cycle = False
            for call in tool_calls:
                func = call.get("function", {})
                name = str(func.get("name", ""))
                raw_args = func.get("arguments") or "{}"
                if isinstance(raw_args, str):
                    try:
                        import json

                        args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        args = {}
                else:
                    args = raw_args
                if not isinstance(args, dict):
                    args = {}

                call_hash = args_hash(name, args)
                recent_calls.append(call_hash)
                if name == "bash":
                    commands_run.append(str(args.get("command", ""))[:300])

                result: ToolResult = execute_tool(name, args, self.workdir)
                files_changed.update(result.changed_files)
                out = result.output
                if len(out) > self.config.max_output_chars:
                    out = out[: self.config.max_output_chars] + "\n...[truncated]"
                if out not in seen_outputs:
                    seen_outputs.add(out)
                    progress_this_cycle = True
                if result.changed_files:
                    progress_this_cycle = True

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": str(call.get("id", "")),
                        "name": name,
                        "content": out,
                    }
                )

            # Repeated-command guard: same call 3 times in a row.
            if len(recent_calls) >= self.config.repeated_command_limit:
                tail = recent_calls[-self.config.repeated_command_limit :]
                if len(set(tail)) == 1:
                    stop_reason = "repeated_command"
                    break

            # No-progress guard.
            if not progress_this_cycle:
                self._no_progress_count = getattr(self, "_no_progress_count", 0) + 1
                if self._no_progress_count >= self.config.no_progress_limit:
                    stop_reason = "no_progress"
                    break
            else:
                self._no_progress_count = 0

            self._trim_context(messages)

        duration = time.time() - started
        report_text = self._build_report(
            task_id, stop_reason, final_content, commands_run, sorted(files_changed), cycles
        )
        return AgentRunResult(
            worker=self.worker,
            task_id=task_id,
            stop_reason=stop_reason,
            decision=self._parse_decision(final_content),
            cycles=cycles,
            commands_run=commands_run,
            files_changed=sorted(files_changed),
            report_text=report_text,
            duration_s=round(duration, 1),
            error=error,
        )

    def _chat_with_retry(self, messages: list[dict[str, object]]) -> dict[str, object] | None:
        delay = 5
        for attempt in range(self.config.max_retries):
            try:
                return self.client.chat(
                    messages,
                    tools=tool_schemas(),
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
            except QwenError:
                if attempt == self.config.max_retries - 1:
                    return None
                time.sleep(delay)
                delay *= 2
        return None

    def _trim_context(self, messages: list[dict[str, object]]) -> None:
        total = sum(len(str(m.get("content") or "")) for m in messages)
        if total <= self.config.context_budget_chars:
            return
        # Truncate the oldest tool results first (keep system, first user, last 6 messages).
        keep_tail = 6
        for index in range(1, len(messages) - keep_tail):
            if total <= self.config.context_budget_chars:
                break
            if messages[index].get("role") == "tool":
                content = str(messages[index].get("content") or "")
                if len(content) > 400:
                    messages[index]["content"] = content[:400] + "\n...[trimmed]"
                    total -= len(content) - 400

    @staticmethod
    def _parse_decision(content: str) -> str | None:
        import re

        match = re.search(r"Decision:\s*(GO|HOLD|KILL|BLOCK)", content, flags=re.IGNORECASE)
        if match:
            return match.group(1).upper()
        match = re.search(r"\b(GO|HOLD|KILL|BLOCK)\b", content)
        return match.group(1).upper() if match else None

    def _build_report(
        self,
        task_id: str | None,
        stop_reason: str,
        final_content: str,
        commands_run: list[str],
        files_changed: list[str],
        cycles: int,
    ) -> str:
        lines = [
            f"# Agent Report: {task_id or 'adhoc'}",
            "",
            f"Generated: {_utc_now()}",
            f"Worker: {self.worker}",
            f"Stop reason: {stop_reason}",
            f"Cycles: {cycles}",
            "",
            "## Final answer",
            "",
            final_content.strip() or "(no final content produced)",
            "",
            "## Commands run",
            "",
        ]
        if commands_run:
            lines.extend(f"- `{c}`" for c in commands_run[-30:])
        else:
            lines.append("(none)")
        lines += ["", "## Files changed", ""]
        if files_changed:
            lines.extend(f"- {p}" for p in files_changed)
        else:
            lines.append("(none)")
        return "\n".join(lines) + "\n"
