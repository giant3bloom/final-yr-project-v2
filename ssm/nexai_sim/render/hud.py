# render/hud.py
import pygame

FONT_SIZE = 16

LABEL_COLOR = (220, 220, 220)
POSITION_VALUE_COLOR = (180, 90, 200)  # purple
DRAG_COLOR = (200, 200, 200)

LINE_SPACING = 6
RIGHT_MARGIN = 330
BOTTOM_MARGIN = 120


class HUD:
    """
    Heads-up display (HUD).

    Layer role in engine architecture:
    - UI / Visualization layer
    - Reads simulation state (Ball)
    - Renders textual diagnostics
    - STRICTLY no simulation or renderer mutation

    Safe for data-driven scenes (scene.json / loader).
    """

    def __init__(self):
        # Ensure pygame font subsystem is initialized
        if not pygame.font.get_init():
            pygame.font.init()

        # Use a monospaced font for stable numeric alignment
        self.font = pygame.font.SysFont("consolas", FONT_SIZE)

        # Cached text fragments (micro-optimization)
        self._comma = ", "
        self._comma_width = self.font.size(self._comma)[0]

    # -------------------------------------------------
    # Color mapping per scalar value (velocity encoding)
    # -------------------------------------------------
    def value_color(self, v, vmax=2.0):
        """
        Map scalar magnitude to RGB gradient.
        Low magnitude -> green
        High magnitude -> red
        """
        t = min(abs(v) / vmax, 1.0)
        return (
            int(255 * t),        # red increases with magnitude
            int(255 * (1 - t)),  # green decreases with magnitude
            180                  # constant blue tint for readability
        )

    # -------------------------------------------------
    def draw(self, screen, ball):
        """
        Render HUD elements.

        Args:
            screen: pygame display surface
            ball: simulation state object (read-only usage)
        """
        # Defensive: avoid rendering if screen is invalid
        if screen is None or ball is None:
            return

        x = screen.get_width() - RIGHT_MARGIN
        y = screen.get_height() - BOTTOM_MARGIN

        # =================================================
        # POSITION (label neutral, values purple)
        # =================================================
        label = "Position : ("
        label_surface = self.font.render(label, True, LABEL_COLOR)
        screen.blit(label_surface, (x, y))

        offset_x = x + label_surface.get_width()

        for i, value in enumerate((
            ball.display_position.x,
            ball.display_position.y,
            ball.display_position.z,
        )):
            txt = f"{value:.2f}"
            txt_surface = self.font.render(txt, True, POSITION_VALUE_COLOR)
            screen.blit(txt_surface, (offset_x, y))
            offset_x += txt_surface.get_width()

            if i < 2:
                comma_surface = self.font.render(self._comma, True, LABEL_COLOR)
                screen.blit(comma_surface, (offset_x, y))
                offset_x += self._comma_width

        closing_surface = self.font.render(")", True, LABEL_COLOR)
        screen.blit(closing_surface, (offset_x, y))

        y += FONT_SIZE + LINE_SPACING

        # =================================================
        # VELOCITY (per-axis color encoding)
        # =================================================
        label = "Velocity : ("
        label_surface = self.font.render(label, True, LABEL_COLOR)
        screen.blit(label_surface, (x, y))

        offset_x = x + label_surface.get_width()

        for i, value in enumerate((
            ball.velocity.x,
            ball.velocity.y,
            ball.velocity.z,
        )):
            txt = f"{value:.2f}"
            color = self.value_color(value)
            txt_surface = self.font.render(txt, True, color)
            screen.blit(txt_surface, (offset_x, y))
            offset_x += txt_surface.get_width()

            if i < 2:
                comma_surface = self.font.render(self._comma, True, LABEL_COLOR)
                screen.blit(comma_surface, (offset_x, y))
                offset_x += self._comma_width

        closing_surface = self.font.render(")", True, LABEL_COLOR)
        screen.blit(closing_surface, (offset_x, y))

        y += FONT_SIZE + LINE_SPACING

        # =================================================
        # DRAG (neutral diagnostic)
        # =================================================
        drag_txt = f"Drag     : {ball.drag:.2f}"
        drag_surface = self.font.render(drag_txt, True, DRAG_COLOR)
        screen.blit(drag_surface, (x, y))
