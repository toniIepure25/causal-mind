from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SystemSnapshot:
    gpu_status: str
    qwen_status: str
    mem_available_gb: float
    disk_free_gb: str


def collect_system_snapshot(root: Path) -> SystemSnapshot:
    gpu_status = _gpu_status()
    qwen_status = _qwen_status()
    mem_available_gb = _mem_available_gb()
    disk_free_gb = _disk_free_gb(root)
    return SystemSnapshot(
        gpu_status=gpu_status,
        qwen_status=qwen_status,
        mem_available_gb=mem_available_gb,
        disk_free_gb=disk_free_gb,
    )


def _gpu_status() -> str:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return "unavailable"
        lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
        if not lines:
            return "no-gpu"
        name, used, total, util = lines[0].split(",")
        return f"{name.strip()} {used.strip()}/{total.strip()}MiB util={util.strip()}%"
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def _qwen_status() -> str:
    import json
    import urllib.request

    try:
        req = urllib.request.Request("http://127.0.0.1:18000/v1/models")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        models = [m.get("id") for m in data.get("data", [])]
        return "healthy" if models else "no-models"
    except (OSError, ValueError):
        return "unreachable"


def _mem_available_gb() -> float:
    try:
        with open("/proc/meminfo", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / (1024 * 1024)
    except (OSError, ValueError, IndexError):
        pass
    return -1.0


def _disk_free_gb(root: Path) -> str:
    try:
        usage = shutil.disk_usage(root)
        return f"{usage.free / (1024**3):.0f}GB"
    except OSError:
        return "unknown"
