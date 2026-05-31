import json
import os
import random
import sys
from pathlib import Path
from threading import Thread

import arcade
import numpy as np
from pynput import keyboard

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import USER_MOVES_DIR, USER_MOVES_FILE, ensure_output_dirs
from demo_engine.assets import funcs, maze_gui, random_maze as maz


def ran_value():
    return random.getrandbits(32)


def main():
    seed = ran_value()
    mat = maz.random_maze(seed)
    maze = maz.expand_with_gaps(mat)

    window = maze_gui.MazeGame(maze)
    moves = []

    def move(direction):
        moves.append(direction)
        window.move_ball(direction)

    def save_run():
        discovered = np.full((10, 10), -1)
        acc = round(funcs.absolute_accuracy(mat, discovered, len(moves)), 2)
        print("No.of.Steps:", len(moves))

        ensure_output_dirs()
        filename = str(USER_MOVES_FILE)

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                all_runs = [json.loads(line) for line in f if line.strip()]
        else:
            all_runs = []

        run_data = {
            "run": len(all_runs) + 1,
            "accuracy": acc,
        }
        all_runs.append(run_data)

        with open(filename, "w", encoding="utf-8") as f:
            for run in all_runs:
                f.write(json.dumps(run, separators=(",", ":")) + "\n")

        print(f"Run {run_data['run']} saved with Accuracy of {run_data['accuracy']}")

    def stop_arcade(delta_time):
        window.close()
        arcade.exit()
        save_run()

    def on_press(key):
        try:
            if key == keyboard.Key.up:
                move("up")
            elif key == keyboard.Key.down:
                move("down")
            elif key == keyboard.Key.left:
                move("left")
            elif key == keyboard.Key.right:
                move("right")
            else:
                print(f"Other key pressed: {key}")
        except AttributeError:
            print(f"Special key pressed: {key}")

    def on_release(key):
        if key == keyboard.Key.esc:
            arcade.schedule_once(stop_arcade, 0)
            return False

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener_thread = Thread(target=listener.start)
    listener_thread.start()

    arcade.run()
    listener_thread.join()


if __name__ == "__main__":
    main()
