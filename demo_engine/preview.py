"""Single maze run with Arcade GUI — ball navigation preview."""
from __future__ import annotations

import random
import sys
import traceback

import arcade

from config import MAX_STEPS, MOVE_TIME


def run_preview(seed: int | None = None, max_steps: int = MAX_STEPS) -> dict:
    result = {
        "success": False,
        "steps_count": 0,
        "error": None,
    }
    try:
        from demo_engine.assets import controller as ctrl
        from demo_engine.assets import maze_gui, random_maze as maz

        if seed is None:
            seed = random.getrandbits(32)

        mat = maz.random_maze(seed)
        maze = maz.expand_with_gaps(mat)
        window = maze_gui.MazeGame(maze)

        step_finder = ctrl.MazeController(maze, (0, 0), max_steps=max_steps)
        steps = step_finder.export()
        step_iter = iter(steps)

        def move_step(delta_time):
            try:
                window.move_ball(next(step_iter))
            except StopIteration:
                arcade.unschedule(move_step)
                window.close()

        arcade.schedule(move_step, MOVE_TIME)
        arcade.run()

        result["success"] = True
        result["steps_count"] = len(steps)
    except Exception:
        result["error"] = traceback.format_exc()

    return result


def main() -> None:
    payload = run_preview()
    if payload["success"]:
        print(f"Preview complete — {payload['steps_count']} steps")
        sys.exit(0)
    print(payload["error"], file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
