
import random
import time

import arcade
import numpy as np

from config import MOVE_TIME, ensure_output_dirs
from demo_engine.assets import maze_gui, random_maze as maz, controller as ctrl, funcs
from demo_engine.discovery import simulate_discovery
from demo_engine.io import file_op as f_op

MAX_STEPS = 450


def ran_value():
    r = random.getrandbits(32)
    if random.choice([True, False]):
        r = -r
    return r


RAN_VALUE = ran_value()


def abs_acc(maze, mat, steps):
    discovered_full = simulate_discovery(maze, steps, start=(0, 0))
    discovered = funcs.strink_matrix(discovered_full)
    return funcs.absolute_accuracy(mat, discovered, len(steps))


def itr(seed):
    mat = maz.random_maze(seed)
    maze = maz.expand_with_gaps(mat)

    window = maze_gui.MazeGame(maze)

    start_t = time.time()
    step_finder = ctrl.MazeController(maze, (0, 0), max_steps=MAX_STEPS)
    end_t = time.time()

    steps = step_finder.export()
    steps_count = len(steps)
    step_iter = iter(steps)

    def move_step(delta_time):
        try:
            step = next(step_iter)
            window.move_ball(step)
        except StopIteration:
            arcade.unschedule(move_step)
            window.close()

    arcade.schedule(move_step, MOVE_TIME)
    arcade.run()

    return [int(end_t - start_t), abs_acc(maze, mat, steps)]


def run(itr_count=10):
    ensure_output_dirs()
    results = []
    for i in range(itr_count):
        results.append(itr(RAN_VALUE))
        print("itr :", i + 1)

    avg_time = round(sum(x[0] for x in results) / len(results), 2)
    avg_acc = round(sum(x[1] for x in results) / len(results), 2)

    f_op.save_as_file(avg_acc)

    return f"Average time: {avg_time}, Average accuracy: {avg_acc}"


if __name__ == "__main__":
    print(run())
