"""Child-process wrappers for isolated NexAI runtime components."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from config import (
    DEMO_ENGINE_MODULE,
    DEMO_PREVIEW_MODULE,
    DEMO_VENV_PYTHON,
    SANDBOX_MODULE,
    SHOW_GUI_PREVIEW,
    STATUS_SHOWER_MODULE,
)
from NexAI.runtime.bootstrap import PROJECT_ROOT as ROOT


def resolve_python(isolated: bool = False) -> Path:
    """Pick interpreter for child processes (optional demo_engine venv)."""
    if isolated and DEMO_VENV_PYTHON.exists():
        return DEMO_VENV_PYTHON
    return Path(sys.executable)


def format_process_error(result: subprocess.CompletedProcess[str]) -> str:
    chunks = [
        result.stderr.strip() if result.stderr else "",
        result.stdout.strip() if result.stdout else "",
    ]
    combined = "\n".join(part for part in chunks if part)
    return combined or f"process exited with code {result.returncode}"


def run_module(
    module: str,
    *,
    isolated: bool = False,
    args: list[str] | None = None,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    cmd = [str(resolve_python(isolated)), "-m", module, *(args or [])]
    return subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=False,
        cwd=str(ROOT),
    )


def run_module_gui(
    module: str,
    *,
    isolated: bool = True,
    args: list[str] | None = None,
) -> subprocess.CompletedProcess[str | None]:
    """Run a module in a visible child process (Arcade window, etc.)."""
    cmd = [str(resolve_python(isolated)), "-m", module, *(args or [])]
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        check=False,
    )
    return proc


def parse_json_stdout(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    """Parse JSON payload from the last stdout line."""
    if not result.stdout.strip():
        raise ValueError(format_process_error(result))

    for line in reversed(result.stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        if line.startswith("__SANDBOX_RESULT__:"):
            return json.loads(line.split(":", 1)[1])
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue

    raise ValueError(format_process_error(result))


class StatusShowerProcess:
    """SSM status dashboard — spawned and destroyed with the optimizer."""

    MODULE = STATUS_SHOWER_MODULE

    def __init__(self, startup_delay: float = 0.6):
        self.startup_delay = startup_delay
        self.proc: subprocess.Popen | None = None

    def start(self) -> None:
        if self.proc and self.proc.poll() is None:
            return

        self.proc = subprocess.Popen(
            [str(resolve_python(False)), "-m", self.MODULE],
            cwd=str(ROOT),
        )
        time.sleep(self.startup_delay)

    def stop(self) -> None:
        if not self.proc or self.proc.poll() is not None:
            self.proc = None
            return

        self.proc.terminate()
        try:
            self.proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=2)
        finally:
            self.proc = None

    def __enter__(self) -> "StatusShowerProcess":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()


class SandboxProcess:
    """Headless demo_engine validation in an isolated child process."""

    MODULE = SANDBOX_MODULE

    @classmethod
    def run(cls) -> dict[str, Any]:
        result = run_module(cls.MODULE, isolated=True)
        try:
            payload = parse_json_stdout(result)
        except ValueError as exc:
            return {
                "success": False,
                "low_collision": False,
                "collision_percentage": None,
                "code score": None,
                "sandbox_error": str(exc),
                "demo_engine_error": None,
            }

        payload.setdefault("success", result.returncode == 0)
        if not payload["success"] and payload.get("error"):
            payload["sandbox_error"] = payload["error"]
            payload["code score"] = None
        return payload


class DemoEngineProcess:
    """Arcade GUI preview — isolated child with visible window."""

    PREVIEW_MODULE = DEMO_PREVIEW_MODULE
    BENCHMARK_MODULE = DEMO_ENGINE_MODULE

    @classmethod
    def run_preview(cls) -> dict[str, Any]:
        if not SHOW_GUI_PREVIEW:
            return {"success": True, "demo_engine_error": None, "code score": None}

        result = run_module_gui(cls.PREVIEW_MODULE, isolated=True)
        if result.returncode != 0:
            return {
                "success": False,
                "demo_engine_error": f"GUI preview exited with code {result.returncode}",
                "code score": None,
            }
        return {
            "success": True,
            "demo_engine_error": None,
            "code score": None,
        }

    @classmethod
    def run(cls) -> dict[str, Any]:
        """Default NexAI demo step: visible single-run GUI preview."""
        return cls.run_preview()
