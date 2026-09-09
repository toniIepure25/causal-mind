from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = os.environ.get("CM_QWEN_BASE_URL", "http://127.0.0.1:18000/v1")
DEFAULT_MODEL = os.environ.get("CM_QWEN_MODEL", "Qwen/Qwen3.8-27B-FP8")


class QwenError(RuntimeError):
    pass


class QwenClient:
    """Minimal OpenAI-compatible client for the local Qwen port-forward."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: int = 300,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {"model": self.model, "messages": messages, **kwargs}
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:500]
            raise QwenError(f"HTTP {exc.code}: {body}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise QwenError(f"endpoint unreachable: {exc}") from exc

    def complete(self, prompt: str, max_tokens: int = 2400) -> str:
        content_prompt = "/no_think\nReturn only the final Markdown report.\n\n" + prompt
        for _ in range(2):
            response = self.chat(
                [{"role": "user", "content": content_prompt}],
                max_tokens=max_tokens,
                temperature=0.2,
                chat_template_kwargs={"enable_thinking": False},
            )
            content = response["choices"][0]["message"].get("content") or ""
            if content.strip():
                return content
            content_prompt = (
                "/no_think\nYour previous response had empty content. "
                "Return the requested Markdown report now.\n\n" + prompt
            )
        raise QwenError("Qwen returned empty content")

    def health(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/models")
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
            return any(m.get("id") == self.model for m in data.get("data", []))
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            return False
