import numpy as np

from NexAI.dynamic.status import log_message
from NexAI.v_sandbox import acc_cal


def verify_wall_collision(maze, start, steps, max_collision_percent):
    rows, cols = len(maze), len(maze[0])
    x, y = start
    total_moves = len(steps)
    collisions = 0

    move = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }

    for step in steps:
        if step not in move:
            continue

        dx, dy = move[step]
        nx, ny = x + dx, y + dy

        if nx < 0 or nx >= rows or ny < 0 or ny >= cols or maze[nx][ny] == 1:
            collisions += 1
        else:
            x, y = nx, ny

    if total_moves != 0:
        collision_percent = (collisions / total_moves) * 100
    else:
        collision_percent = 100
        print("no-moves made")

    print(f"Total steps: {total_moves}")
    print(f"Collisions: {collisions} ({collision_percent:.2f}%)")

    if collision_percent <= max_collision_percent:
        log_message("Within acceptable limit", True)
        return [True, collision_percent]

    log_message("Too many wall collisions", True)
    return [False, collision_percent]


def abs_acc(maze, steps_count):
    discovered = -np.ones_like(maze)
    return acc_cal.absolute_accuracy(maze, discovered, steps_count)
