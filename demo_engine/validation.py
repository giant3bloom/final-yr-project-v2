"""Collision checks for sandbox validation."""
from __future__ import annotations


def verify_wall_collision(maze, start, steps, max_collision_percent, *, quiet: bool = False):
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
        collision_percent = 100.0
        if not quiet:
            print("no-moves made", file=__import__("sys").stderr)

    if not quiet:
        print(f"Total steps: {total_moves}", file=__import__("sys").stderr)
        print(
            f"Collisions: {collisions} ({collision_percent:.2f}%)",
            file=__import__("sys").stderr,
        )

    low_collision = collision_percent <= max_collision_percent
    return [low_collision, collision_percent]
