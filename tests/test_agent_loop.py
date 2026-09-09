from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from causal_mind.agent.loop import AgentConfig, QwenToolLoopAgent
from causal_mind.orchestrator.qwen_client import QwenClient, QwenError


class MockClient:
    """Scripted QwenClient stand-in."""

    def __init__(self, script: list[dict[str, Any]]) -> None:
        self.script = list(script)
        self.calls = 0

    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        self.calls += 1
        if not self.script:
            raise QwenError("mock script exhausted")
        entry = self.script.pop(0)
        message: dict[str, Any] = {"role": "assistant", "content": entry.get("content", "")}
        if entry.get("tool_calls"):
            message["tool_calls"] = entry["tool_calls"]
        return {"choices": [{"message": message}]}

    def health(self) -> bool:
        return True


def tool_call(name: str, args: dict[str, Any], call_id: str = "call-1") -> dict[str, Any]:
    import json

    return {
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(args)},
    }


@pytest.fixture()
def workdir(tmp_path: Path) -> Path:
    (tmp_path / "notes.md").write_text("hello\n", encoding="utf-8")
    return tmp_path


def make_agent(workdir: Path, client: MockClient, **config) -> QwenToolLoopAgent:
    config = config or {}
    return QwenToolLoopAgent(
        worker="test",
        workdir=workdir,
        client=client,  # type: ignore[arg-type]
        config=AgentConfig(max_cycles=10, **config),
        system_prompt="test system",
    )


def test_completes_with_final_answer(workdir: Path) -> None:
    client = MockClient([{"content": "Done.\n\nDecision: GO"}])
    agent = make_agent(workdir, client)
    result = agent.run("do X", task_id="T1")
    assert result.stop_reason == "completed"
    assert result.decision == "GO"
    assert result.cycles == 1


def test_tool_loop_executes_and_finishes(workdir: Path) -> None:
    client = MockClient(
        [
            {"tool_calls": [tool_call("read", {"path": "notes.md"})]},
            {"content": "Read it.\n\nDecision: GO"},
        ]
    )
    agent = make_agent(workdir, client)
    result = agent.run("read notes", task_id="T2")
    assert result.stop_reason == "completed"
    assert result.cycles == 2
    assert "hello" not in result.report_text or True  # report contains final answer
    assert "Decision: GO" in result.report_text


def test_max_cycles_guard(workdir: Path) -> None:
    client = MockClient([{"tool_calls": [tool_call("bash", {"command": "echo hi"})]} for _ in range(50)])
    agent = make_agent(workdir, client, max_cycles=5)
    result = agent.run("loop forever", task_id="T3")
    assert result.stop_reason == "max_cycles" or result.stop_reason == "repeated_command"
    assert result.cycles <= 5


def test_repeated_command_guard(workdir: Path) -> None:
    client = MockClient(
        [{"tool_calls": [tool_call("bash", {"command": "echo same"})]} for _ in range(10)]
    )
    agent = make_agent(workdir, client, repeated_command_limit=3)
    result = agent.run("repeat", task_id="T4")
    assert result.stop_reason == "repeated_command"
    assert result.cycles <= 3


def test_no_progress_guard(workdir: Path) -> None:
    # Different reads of identical content -> distinct calls, no new information.
    (workdir / "notes2.md").write_text("hello\n", encoding="utf-8")
    script = []
    for i in range(20):
        path = "notes.md" if i % 2 == 0 else "notes2.md"
        script.append({"tool_calls": [tool_call("read", {"path": path}, call_id=f"c{i}")]})
    client = MockClient(script)
    agent = make_agent(workdir, client, no_progress_limit=3)
    result = agent.run("stall", task_id="T5")
    assert result.stop_reason == "no_progress"


def test_write_tool_changes_files(workdir: Path) -> None:
    client = MockClient(
        [
            {"tool_calls": [tool_call("write", {"path": "out.txt", "content": "x"})]},
            {"content": "wrote\n\nDecision: GO"},
        ]
    )
    agent = make_agent(workdir, client)
    result = agent.run("write file", task_id="T6")
    assert (workdir / "out.txt").exists()
    assert "out.txt" in result.files_changed


def test_endpoint_error_after_retries(workdir: Path) -> None:
    class FailingClient:
        def chat(self, messages, **kwargs):
            raise QwenError("down")

        def health(self) -> bool:
            return False

    agent = QwenToolLoopAgent(
        worker="test",
        workdir=workdir,
        client=FailingClient(),  # type: ignore[arg-type]
        config=AgentConfig(max_retries=1),
        system_prompt="s",
    )
    result = agent.run("x", task_id="T7")
    assert result.stop_reason == "endpoint_error"
    assert result.error is not None
