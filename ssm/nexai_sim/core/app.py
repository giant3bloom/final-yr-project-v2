# core/app.py

from nexai_sim.physics.ball import Ball


class App:
    """
    Application state coordinator.

    Responsibilities:
    - Owns simulation objects (Ball)
    - Updates state using a fixed timestep
    - Accepts externally constructed entities (scene-driven)
    - Contains NO rendering logic
    """

    def __init__(self, ball: Ball | None = None):
        """
        Initialize application state.

        Args:
            ball (Ball | None):
                Injected ball from scene loader (data-driven).
                Falls back to default Ball() if not provided.
        """
        # Scene-driven injection (compiler-style architecture)
        self.ball = ball if ball is not None else Ball()

        # Fixed timestep (seconds)
        self.dt = 0.016

    def update(self):
        """Update application state."""
        self.ball.update(self.dt)
