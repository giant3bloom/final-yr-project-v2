# render/pygame_renderer.py
import pygame
import math

from nexai_sim.math3d.vec3 import Vec3
from nexai_sim.render.mesh import generate_sphere
from nexai_sim.render.projection import project

# -------------------------------------------------
# Screen / projection
WIDTH, HEIGHT = 800, 600
SCALE = 400

# Motion pointer visuals
ARROW_SCALE = 40
ARROW_MAX_LEN = 55

# Axis guide visuals
AXIS_LEN = 60
AXIS_ORIGIN_XY = (100, 100)
AXIS_ORIGIN_Z = (100, 190)
# -------------------------------------------------


class PygameRenderer:
    """
    Pygame-based renderer (read-only rendering backend).

    Responsibilities:
    - Render polygon mesh sphere
    - Apply showcase rotation (visual only)
    - Draw axis guides and motion arrows
    - NEVER mutate simulation state

    Compatible with:
    - Scene-driven Ball injection
    - Data-driven engine architecture
    """

    def __init__(self):
        pygame.init()

        # ---- window ----
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("NEXAI – Showcase Ball")
        self.clock = pygame.time.Clock()

        # ---- fonts (created once) ----
        if not pygame.font.get_init():
            pygame.font.init()
        self.axis_font = pygame.font.SysFont("consolas", 14)

        # ---- mesh (procedural sphere geometry) ----
        self.vertices, self.faces = generate_sphere(
            radius=0.5,
            lat_steps=16,
            lon_steps=16
        )

        # ---- showcase rotation (visual only) ----
        self.rotation = 0.0
        self.rotation_speed = 0.4
        self.ball_scale = 3.0  # Visual scale multiplier

    # -------------------------------------------------
    def begin_frame(self):
        """Clear frame buffer."""
        self.screen.fill((12, 12, 18))

    # -------------------------------------------------
    def update_rotation(self, dt):
        """Update showcase rotation (purely visual)."""
        if dt > 0.0:
            self.rotation += self.rotation_speed * dt

    # -------------------------------------------------
    def draw_mesh_ball(self, ball):
        """
        Render the ball mesh using projection pipeline.

        NOTE:
        - Uses ball.position as fixed world anchor
        - Does NOT modify ball state (strictly read-only)
        """
        projected = []

        cos_r = math.cos(self.rotation)
        sin_r = math.sin(self.rotation)

        # ---- project vertices (Model -> World -> Screen) ----
        for v in self.vertices:
            # Scale mesh
            vx = v.x * self.ball_scale
            vy = v.y * self.ball_scale
            vz = v.z * self.ball_scale

            # Y-axis rotation (showcase spin)
            rx = vx * cos_r - vz * sin_r
            rz = vx * sin_r + vz * cos_r

            # World transform (anchored to ball.position)
            world_v = Vec3(rx, vy, rz) + ball.position

            # Projection (3D -> 2D)
            projected.append(
                project(world_v, WIDTH, HEIGHT, SCALE)
            )

        # ---- draw faces safely ----
        count = len(projected)
        for face in self.faces:
            if any(i >= count for i in face):
                continue

            pts = [projected[i] for i in face]

            pygame.draw.polygon(
                self.screen,
                (60, 140, 255),  # Blue wireframe ball
                pts,
                1
            )

    # -------------------------------------------------
    def draw_arrow_line(self, start, end, color=(230, 230, 230), width=3):
        """Draw directional arrow line (UI visualization)."""
        pygame.draw.line(self.screen, color, start, end, width)

        # ---- arrowhead ----
        angle = math.atan2(start[1] - end[1], end[0] - start[0])
        head_len = 10

        left = (
            end[0] - head_len * math.cos(angle + math.pi / 6),
            end[1] + head_len * math.sin(angle + math.pi / 6),
        )
        right = (
            end[0] - head_len * math.cos(angle - math.pi / 6),
            end[1] + head_len * math.sin(angle - math.pi / 6),
        )

        pygame.draw.polygon(self.screen, color, [end, left, right])

    # -------------------------------------------------
    def draw_axis_guides(self):
        """Draw XYZ axis reference guides."""
        # ===== XY AXES =====
        ox, oy = AXIS_ORIGIN_XY

        # X axis (red)
        pygame.draw.line(
            self.screen, (255, 80, 80),
            (ox, oy),
            (ox + AXIS_LEN, oy),
            2
        )
        self.screen.blit(
            self.axis_font.render("X", True, (255, 80, 80)),
            (ox + AXIS_LEN + 6, oy - 6)
        )

        # Y axis (green)
        pygame.draw.line(
            self.screen, (80, 255, 80),
            (ox, oy),
            (ox, oy - AXIS_LEN),
            2
        )
        self.screen.blit(
            self.axis_font.render("Y", True, (80, 255, 80)),
            (ox - 12, oy - AXIS_LEN - 14)
        )

        # ===== Z AXIS =====
        ozx, ozy = AXIS_ORIGIN_Z

        pygame.draw.line(
            self.screen, (80, 80, 255),
            (ozx, ozy),
            (ozx, ozy - AXIS_LEN),
            2
        )
        self.screen.blit(
            self.axis_font.render("Z", True, (80, 80, 255)),
            (ozx - 12, ozy - AXIS_LEN - 14)
        )

    # -------------------------------------------------
    def draw_motion_pointers(self, ball):
        """Visualize velocity vectors (debug UI)."""
        self.draw_axis_guides()

        # ===== XY POINTER =====
        ox, oy = AXIS_ORIGIN_XY
        vx, vy = ball.velocity.x, ball.velocity.y

        dx = vx * ARROW_SCALE
        dy = -vy * ARROW_SCALE

        length = math.hypot(dx, dy)
        if length > ARROW_MAX_LEN and length > 0:
            scale_factor = ARROW_MAX_LEN / length
            dx *= scale_factor
            dy *= scale_factor

        end_xy = (ox + int(dx), oy + int(dy))

        self.draw_arrow_line((ox, oy), end_xy)
        pygame.draw.circle(self.screen, (220, 220, 220), (ox, oy), 4)

        # ===== Z POINTER =====
        ozx, ozy = AXIS_ORIGIN_Z
        vz = ball.velocity.z

        dz = -vz * ARROW_SCALE
        dz = max(-ARROW_MAX_LEN, min(ARROW_MAX_LEN, dz))

        end_z = (ozx, ozy + int(dz))

        self.draw_arrow_line((ozx, ozy), end_z)
        pygame.draw.circle(self.screen, (220, 220, 220), (ozx, ozy), 4)

    # -------------------------------------------------
    def end_frame(self):
        """Present frame and cap FPS."""
        pygame.display.flip()
        self.clock.tick(60)
