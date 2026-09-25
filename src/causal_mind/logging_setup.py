"""Structured logging setup (CM-REPO S14).

:func:`config_logging` returns a logger that emits one JSON object per line
when ``CM_LOG_JSON=1`` (machine-parseable for CI / log aggregation) and a
human-readable one-line format otherwise. Every field is stable so downstream
tooling can rely on it.

Usage::

    from causal_mind.logging_setup import config_logging
    log = config_logging("cm.validate")          # name = component
    log.info("checks complete", extra={"run_id": rid, "passed": 12})
"""
from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Merge any structured fields passed via extra={...}
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


_RESERVED = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName", "processName",
    "process", "taskName", "message",
}


def config_logging(name: str, *, json_output: bool | None = None, level: int = logging.INFO) -> logging.Logger:
    """Configure and return a logger for ``name``.

    ``json_output`` defaults to ``CM_LOG_JSON=1``. Repeated calls are safe
    (idempotent): handlers are not duplicated.
    """
    if json_output is None:
        json_output = os.environ.get("CM_LOG_JSON") == "1"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        if json_output:
            handler.setFormatter(_JsonFormatter())
        else:
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)-7s %(name)s :: %(message)s")
            )
        logger.addHandler(handler)
    return logger
