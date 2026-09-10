from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from causal_mind.orchestrator.qwen_client import QwenClient, QwenError


class FakeVLLM(BaseHTTPRequestHandler):
    fail_times: int = 0

    def log_message(self, *args: Any) -> None:  # silence
        pass

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/v1/models":
            body = json.dumps({"data": [{"id": "Qwen/Qwen3.8-27B-FP8"}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        if FakeVLLM.fail_times > 0:
            FakeVLLM.fail_times -= 1
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error": "boom"}')
            return
        body = json.dumps(
            {
                "choices": [
                    {"message": {"role": "assistant", "content": "OK", "tool_calls": None}}
                ]
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture()
def server():
    FakeVLLM.fail_times = 0
    httpd = HTTPServer(("127.0.0.1", 0), FakeVLLM)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}/v1"
    httpd.shutdown()


def test_health(server: str) -> None:
    client = QwenClient(base_url=server)
    assert client.health() is True


def test_chat(server: str) -> None:
    client = QwenClient(base_url=server)
    response = client.chat([{"role": "user", "content": "hi"}], max_tokens=8)
    assert response["choices"][0]["message"]["content"] == "OK"


def test_complete_retries_on_empty(server: str) -> None:
    client = QwenClient(base_url=server)
    text = client.complete("prompt", max_tokens=8)
    assert text == "OK"


def test_error_raises(server: str) -> None:
    FakeVLLM.fail_times = 99
    client = QwenClient(base_url=server)
    with pytest.raises(QwenError):
        client.chat([{"role": "user", "content": "hi"}])
    FakeVLLM.fail_times = 0


def test_unreachable() -> None:
    client = QwenClient(base_url="http://127.0.0.1:1/v1", timeout=2)
    assert client.health() is False
    with pytest.raises(QwenError):
        client.chat([{"role": "user", "content": "hi"}])
