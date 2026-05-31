# physics/ball.py

from nexai_sim.math3d.vec3 import Vec3


class Ball:
    """
    Showcase ball state container.

    Design role:
    - Pure simulation state (no rendering logic)
    - Deterministic update step
    - Compatible with scene-driven initialization

    Notes:
    - `position` is a FIXED render anchor (mesh never moves)
    - `velocity` is a vector used for visualization & UI only
    - `display_position` is a logical position derived from velocity
    - No mass, no gravity, no real physics (intentional showcase model)
    """

    def __init__(self):
        # Render anchor (never changes)
        self.position = Vec3(0.0, 0.0, 0.0)

        # Velocity vector (x, y, z)
        self.velocity = Vec3(1.2, 0.8, 0.5)

        # Linear drag coefficient
        self.drag = 0.25

        # Display-only integrated position
        self.display_position = Vec3(0.0, 0.0, 0.0)

        # Threshold to kill tiny drift (numerical stability)
        self._epsilon = 1e-4

    def update(self, dt: float):
        """
        Update ball state.

        Simulation model:
        - Applies linear drag to velocity
        - Integrates velocity into display_position only
        - Keeps render anchor (position) fixed

        Args:
            dt (float): Fixed timestep in seconds
        """

        # Defensive: dt must be positive for stable integration
        if dt <= 0.0:
            return

        # -------- Apply linear drag (per-axis damping) --------
        self.velocity.x -= self.drag * self.velocity.x * dt
        self.velocity.y -= self.drag * self.velocity.y * dt
        self.velocity.z -= self.drag * self.velocity.z * dt

        # -------- Kill tiny drift (floating-point stability) --------
        if abs(self.velocity.x) < self._epsilon:
            self.velocity.x = 0.0
        if abs(self.velocity.y) < self._epsilon:
            self.velocity.y = 0.0
        if abs(self.velocity.z) < self._epsilon:
            self.velocity.z = 0.0

        # -------- Integrate into display-only position --------
        # (Renderer can choose whether to use this or anchor position)
        self.display_position += self.velocity * dt
