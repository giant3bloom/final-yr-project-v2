"""Simulate 3x3 visibility discovery by replaying controller moves on a maze."""
from __future__ import annotations

import numpy as np

MOVE_DELTAS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


def reveal_area(
    maze: np.ndarray,
    discovered: np.ndarray,
    row: int,
    col: int,
    radius: int = 1,
) -> None:
    rows, cols = maze.shape
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                discovered[nr, nc] = maze[nr, nc]


def simulate_discovery(
    maze: np.ndarray,
    steps: list[str],
    start: tuple[int, int] = (0, 0),
) -> np.ndarray:
    """Return discovered map (-1 unknown, 0/1 known) after replaying steps from start."""
    discovered = -np.ones_like(maze)
    row, col = start
    reveal_area(maze, discovered, row, col)

    for step in steps:
        delta = MOVE_DELTAS.get(step)
        if delta is None:
            continue
        dr, dc = delta
        nr, nc = row + dr, col + dc
        if 0 <= nr < maze.shape[0] and 0 <= nc < maze.shape[1] and maze[nr, nc] == 0:
            row, col = nr, nc
            reveal_area(maze, discovered, row, col)

    return discovered
