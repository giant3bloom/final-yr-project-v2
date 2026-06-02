"""Headless sandbox — validates controller code in isolation from NexAI."""
from __future__ import annotations

import json
import sys
import traceback

from config import MAX_STEPS


def run_sandbox(max_steps: int = MAX_STEPS, max_collision_percent: float = 10.1) -> dict:
    result = {
        "success": False,
        "low_collision": False,
        "collision_percentage": None,
        "code score": None,
        "error": None,
        "sandbox_error": None,
        "demo_engine_error": None,
        "steps_count": None,
    }

    try:
        import numpy as np

        from demo_engine.assets import controller, funcs, random_maze as maz
        from demo_engine.discovery import simulate_discovery
        from demo_engine.validation import verify_wall_collision

        mat = maz.random_maze()
        maze = maz.expand_with_gaps(mat)

        ctrl = controller.MazeController(maze, start=(0, 0), max_steps=max_steps)
        steps = ctrl.export()

        collision = verify_wall_collision(
            maze, (0, 0), steps, max_collision_percent, quiet=True
        )
        discovered_full = simulate_discovery(maze, steps, start=(0, 0))
        discovered = funcs.strink_matrix(discovered_full)
        acc_val = round(float(funcs.absolute_accuracy(mat, discovered, len(steps))), 2)

        result.update(
            {
                "success": True,
                "low_collision": bool(collision[0]),
                "collision_percentage": float(collision[1]),
                "code score": acc_val,
                "steps_count": len(steps),
            }
        )
    except Exception:
        result["error"] = traceback.format_exc()
        result["sandbox_error"] = result["error"]
        result["code score"] = None

    return result


def main() -> None:
    payload = run_sandbox()
    print("__SANDBOX_RESULT__:" + json.dumps(payload), flush=True)
    sys.exit(0 if payload["success"] else 1)


if __name__ == "__main__":
    main()
