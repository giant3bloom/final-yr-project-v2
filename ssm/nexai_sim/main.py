# main.py
import pygame
from pathlib import Path

from nexai_sim.core.app import App
from nexai_sim.render.pygame_renderer import PygameRenderer
from nexai_sim.render.hud import HUD
from nexai_sim.scene.loader import load_scene


def main():
    """
    Engine entry point.

    Pipeline:
        scene.json → loader → Ball (entity)
                   → App (state coordinator)
                   → Renderer (read-only visualization)
    """

    # -------------------------------------------------
    # Resolve scene path safely (engine-safe)
    # -------------------------------------------------
    base_dir = Path(__file__).resolve().parent
    scene_path = base_dir / "scene.json"

    # Load scene definition (data-driven entity)
    ball = load_scene(str(scene_path))

    # -------------------------------------------------
    # Setup engine components
    # -------------------------------------------------
    app = App(ball=ball)
    renderer = PygameRenderer()
    hud = HUD()

    running = True
    INPUT_STEP = 0.6  # velocity change per second

    # -------------------------------------------------
    # Main loop
    # -------------------------------------------------
    while running:
        renderer.begin_frame()

        # -------- EVENTS --------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        # -------- INPUT (velocity control) --------
        # X axis
        if keys[pygame.K_LEFT]:
            app.ball.velocity.x -= INPUT_STEP * app.dt
        if keys[pygame.K_RIGHT]:
            app.ball.velocity.x += INPUT_STEP * app.dt

        # Y axis
        if keys[pygame.K_UP]:
            app.ball.velocity.y += INPUT_STEP * app.dt
        if keys[pygame.K_DOWN]:
            app.ball.velocity.y -= INPUT_STEP * app.dt

        # Z axis
        if keys[pygame.K_q]:
            app.ball.velocity.z += INPUT_STEP * app.dt
        if keys[pygame.K_e]:
            app.ball.velocity.z -= INPUT_STEP * app.dt

        # -------- UPDATE (simulation layer) --------
        app.update()
        renderer.update_rotation(app.dt)

        # -------- RENDER (read-only visualization) --------
        renderer.draw_mesh_ball(app.ball)
        renderer.draw_motion_pointers(app.ball)
        hud.draw(renderer.screen, app.ball)

        renderer.end_frame()

    pygame.quit()


if __name__ == "__main__":
    main()
