###optimization-start
from collections import deque
class MazeController:
    def __init__(self, maze, start=(0, 0), max_steps=450):
        self.m, self.p, self.mx, self.mv = maze, start, max_steps, []
    def export(self):
        u = {(r, c) for r in range(21) for c in range(21) if self.m[r, c] == 0}
        def v(p):
            for r in range(p[0] - 1, p[0] + 2):
                for c in range(p[1] - 1, p[1] + 2):
                    u.discard((r, c))
        v(self.p)
        while u and len(self.mv) < self.mx:
            q = deque([(self.p, [])])
            vis = {self.p}
            found = None
            while q:
                curr, path = q.popleft()
                if any((curr[0] + i, curr[1] + j) in u for i in (-1, 0, 1) for j in (-1, 0, 1)):
                    found = (curr, path)
                    break
                for dr, dc, move in [(-1, 0, "up"), (1, 0, "down"), (0, -1, "left"), (0, 1, "right")]:
                    nr, nc = curr[0] + dr, curr[1] + dc
                    if 0 <= nr < 21 and 0 <= nc < 21 and self.m[nr, nc] == 0 and (nr, nc) not in vis:
                        vis.add((nr, nc))
                        q.append(((nr, nc), path + [move]))
            if not found:
                break
            target, path = found
            for m in path:
                self.mv.append(m)
                dr, dc = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[m]
                self.p = (self.p[0] + dr, self.p[1] + dc)
                v(self.p)
        return self.mv
###optimization-end

if __name__ == "__main__":
    from demo_engine.assets import random_maze as maz

    mat = maz.random_maze()
    maze = maz.expand_with_gaps(mat)
    ctrl = MazeController(maze, start=(0, 0), max_steps=200)
    steps = ctrl.export()
    print("Move sequence length:", len(steps))
    print("steps:", steps)
