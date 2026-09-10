from __future__ import annotations

import json
import subprocess
import urllib.request

BASE_URL = "http://127.0.0.1:18000/v1"
MODEL_ID = "Qwen/Qwen3.8-27B-FP8"


def post_chat(payload: dict) -> dict:
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    messages = [
        {
            "role": "user",
            "content": "Use the shell_pwd tool, then answer exactly TOOL-OK if it succeeded.",
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "shell_pwd",
                "description": "Return the current working directory.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        }
    ]
    first = post_chat(
        {
            "model": MODEL_ID,
            "messages": messages,
            "tools": tools,
            "tool_choice": {"type": "function", "function": {"name": "shell_pwd"}},
            "max_tokens": 256,
        }
    )
    assistant = first["choices"][0]["message"]
    tool_calls = assistant.get("tool_calls") or []
    if not tool_calls:
        raise SystemExit(f"no tool call returned: {first}")

    result = subprocess.check_output(["pwd"], text=True).strip()
    messages.append(assistant)
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_calls[0]["id"],
            "name": "shell_pwd",
            "content": result,
        }
    )
    second = post_chat({"model": MODEL_ID, "messages": messages, "max_tokens": 128})
    content = second["choices"][0]["message"].get("content") or ""
    print(json.dumps({"tool_result": result, "final": content}, ensure_ascii=False))
    if "TOOL-OK" not in content:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
