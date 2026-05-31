"""NexAI optimization orchestrator."""
from __future__ import annotations

import traceback
import threading
from typing import Any

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    PROFILER_PORT,
    SHOW_GUI_PREVIEW,
    STATUS_HOST,
    STATUS_PORT,
)
from NexAI.dynamic.status import log_message
from NexAI.hardware_profiler import profile
from NexAI.recreator import model
from NexAI.runtime.processes import (
    DemoEngineProcess,
    SandboxProcess,
    StatusShowerProcess,
)


def empty_feedback() -> dict[str, Any]:
    return {
        "low_collision": False,
        "collision_percentage": None,
        "code score": None,
        "sandbox_error": None,
        "demo_engine_error": None,
        "llm_error": None,
    }


def merge_sandbox_feedback(
    base: dict[str, Any],
    sandbox: dict[str, Any],
) -> dict[str, Any]:
    feedback = empty_feedback()
    feedback.update(base)

    for key in ("low_collision", "collision_percentage", "code score", "sandbox_error"):
        if key in sandbox:
            feedback[key] = sandbox[key]

    if sandbox.get("error") and not feedback.get("sandbox_error"):
        feedback["sandbox_error"] = sandbox["error"]
        feedback["code score"] = None

    return feedback


def single_itr(
    optimizer: model.AdaptiveMazeBlockOptimizer,
    pending_demo_error: str | None = None,
    pending_llm_error: str | None = None,
) -> dict[str, Any]:
    feedback = empty_feedback()
    if pending_demo_error:
        feedback["demo_engine_error"] = pending_demo_error
    if pending_llm_error:
        feedback["llm_error"] = pending_llm_error

    log_message("maze-creation", True, phase="sandbox")
    log_message("sandbox subprocess starting", True, phase="sandbox")

    sandbox = SandboxProcess.run()
    feedback = merge_sandbox_feedback(feedback, sandbox)

    if sandbox.get("success"):
        score = feedback.get("code score")
        collision_pct = feedback.get("collision_percentage")

        log_message(
            "sandbox validation",
            True,
            phase="sandbox",
            score=score,
            clear_error=True,
        )

        if not feedback.get("low_collision"):
            log_message(
                f"collision high ({collision_pct}%) — optimizing",
                False,
                phase="sandbox",
                score=score,
            )

        if SHOW_GUI_PREVIEW:
            log_message("gui preview starting", True, phase="demo_engine")
            preview = DemoEngineProcess.run_preview()
            if not preview["success"]:
                feedback["demo_engine_error"] = preview.get("demo_engine_error")
                feedback["code score"] = None
                log_message(
                    "gui preview",
                    False,
                    phase="demo_engine",
                    score=None,
                    error=preview.get("demo_engine_error"),
                )
            else:
                log_message("gui preview", True, phase="demo_engine", clear_error=True)

        log_message("code-generation", True, phase="llm", score=score)
        if not optimizer.optimize_block(feedback):
            feedback["llm_error"] = feedback.get("llm_error") or "LLM step failed"
            log_message(
                "code-generation",
                False,
                phase="llm",
                score=score,
                error=feedback["llm_error"],
            )
        else:
            log_message("code-generation", True, phase="llm", score=score)

        return feedback

    error_text = feedback.get("sandbox_error") or "Sandbox crashed"
    feedback["code score"] = None
    log_message(
        "sandbox validation",
        False,
        phase="sandbox",
        score=None,
        error=error_text,
    )
    log_message("code-generation", False, phase="llm", score=None, error=error_text)
    if not optimizer.optimize_block(feedback):
        feedback["llm_error"] = feedback.get("llm_error") or "LLM step failed"
    return feedback


def run_demo_engine() -> dict[str, Any]:
    log_message("demo-engine gui preview", True, phase="demo_engine")
    result = DemoEngineProcess.run_preview()

    if result["success"]:
        log_message("demo-engine-runner", True, phase="demo_engine", clear_error=True)
    else:
        log_message(
            "demo-engine-runner",
            False,
            phase="demo_engine",
            score=None,
            error=result.get("demo_engine_error"),
        )

    return result


def main() -> None:
    from NexAI.runtime.bootstrap import bootstrap

    bootstrap()

    shower = StatusShowerProcess()

    try:
        shower.start()
        log_message("system initiated", True, phase="startup")
        profile.send_system_data(STATUS_HOST, PROFILER_PORT)

        log_message("model build", True, phase="startup")
        optimizer = model.AdaptiveMazeBlockOptimizer(GEMINI_API_KEY, GEMINI_MODEL)

        log_message("optimizer ready", True, phase="startup")
        print("Optimizer loop running — type 'exit' and Enter to stop.")

        exit_signal = False

        def input_thread() -> None:
            nonlocal exit_signal
            while True:
                try:
                    user_input = input()
                except EOFError:
                    break
                if user_input.strip().lower() == "exit":
                    exit_signal = True
                    break

        threading.Thread(target=input_thread, daemon=True).start()

        pending_demo_error: str | None = None
        pending_llm_error: str | None = None
        iteration = 0

        while not exit_signal:
            iteration += 1
            print(f"\n--- iteration {iteration} ---")
            log_message(f"iteration {iteration}", True, phase="startup")

            try:
                feedback = single_itr(
                    optimizer,
                    pending_demo_error,
                    pending_llm_error,
                )
                pending_demo_error = None
                pending_llm_error = feedback.get("llm_error")

                demo_result = run_demo_engine()
                if not demo_result["success"]:
                    pending_demo_error = demo_result.get("demo_engine_error")

            except KeyboardInterrupt:
                print("\n[LOG] Interrupted — continuing next iteration (type 'exit' to stop)")
                continue
            except Exception:
                err = traceback.format_exc()
                print(err)
                log_message(
                    "iteration crashed",
                    False,
                    phase="startup",
                    error=err[:500],
                )
                pending_llm_error = err
                continue

    finally:
        log_message("shutting down", True, phase="shutdown")
        shower.stop()
