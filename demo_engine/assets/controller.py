###optimization-start
import collections
class MazeController:
    def __init__(self, maze, start=(0, 0), max_steps=450):
        self.m, self.p, self.mx = maze, start, max_steps
    def export(self):
        u = {(r, c) for r in range(21) for c in range(21) if self.m[r, c] == 0}
        mv = []
        def v(p):
            for r in range(p[0] - 1, p[0] + 2):
                for c in range(p[1] - 1, p[1] + 2):
                    u.discard((r, c))
        v(self.p)
        while u and len(mv) < self.mx:
            q = collections.deque([(self.p, [])])
            vis = {self.p}
            reach = {}
            while q:
                c, path = q.popleft()
                reach[c] = (len(path), path)
                for dr, dc, mn in [(-1, 0, "up"), (1, 0, "down"), (0, -1, "left"), (0, 1, "right")]:
                    nr, nc = c[0] + dr, c[1] + dc
                    if 0 <= nr < 21 and 0 <= nc < 21 and self.m[nr, nc] == 0 and (nr, nc) not in vis:
                        vis.add((nr, nc))
                        q.append(((nr, nc), path + [mn]))
            bc, bp, ms = None, None, -1
            for c, (d, path) in reach.items():
                g = sum(1 for r in range(c[0] - 1, c[0] + 2) for col in range(c[1] - 1, c[1] + 2) if (r, col) in u)
                if g > 0:
                    s = g / (d + 1)**1.1
                    if s > ms: ms, bc, bp = s, c, path
            if not bc: break
            for m in bp:
                mv.append(m)
                dr, dc = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[m]
                self.p = (self.p[0] + dr, self.p[1] + dc)
                v(self.p)
                if not u: break
                if sum(1 for r in range(bc[0] - 1, bc[0] + 2) for col in range(bc[1] - 1, bc[1] + 2) if (r, col) in u) == 0:
                    break
                if len(mv) >= self.mx: break
        return mv
###optimization-end

if __name__ == "__main__":
    from demo_engine.assets import random_maze as maz

    mat = maz.random_maze()
    maze = maz.expand_with_gaps(mat)
    ctrl = MazeController(maze, start=(0, 0), max_steps=450)
    steps = ctrl.export()
    print("Move sequence length:", len(steps))
    print("steps:", steps)
