import arcade
import numpy as np


# ===== Arcade Window =====
class MazeGame(arcade.Window):
    def __init__(self, maze, cell_size = 30):
        self.cell_size = cell_size
        super().__init__(maze.shape[1]*self.cell_size, maze.shape[0]*self.cell_size, "Maze")
        self.maze = maze
        self.rows, self.cols = maze.shape
        self.ball_row, self.ball_col = 0, 0
        self.ball_pos = (0, 0)
        self.discovered = -np.ones_like(maze)
        self.reveal_area(self.ball_row, self.ball_col)
    
    # ===== Discovered map =====
    # -1 = undiscovered, 0 = empty, 1 = wall
    def reveal_area(self, r, c, radius=1):
        for dr in range(-radius, radius+1):
            for dc in range(-radius, radius+1):
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    self.discovered[nr, nc] = self.maze[nr, nc]

    def on_draw(self):
        """Draw the maze and ball."""
        self.clear()  # clear screen before drawing

        for r in range(self.rows):
            for c in range(self.cols):
                x = c * self.cell_size
                y = self.height - (r+1) * self.cell_size
                if self.discovered[r, c] == -1:
                    color = arcade.color.DARK_GRAY  # undiscovered
                elif self.discovered[r, c] == 1:
                    color = arcade.color.BLACK      # wall
                else:
                    color = arcade.color.LIGHT_GRAY # empty space
                # Draw filled rectangle
                arcade.draw_lrbt_rectangle_filled(
                    x, x + self.cell_size, y, y + self.cell_size, color
                )
                # Draw grid outline
                arcade.draw_lrbt_rectangle_outline(
                    x, x + self.cell_size, y, y + self.cell_size, arcade.color.GRAY
                )

        # Draw ball
        ball_x = self.ball_pos[0] * self.cell_size + self.cell_size // 2
        ball_y = self.height - (self.ball_pos[1] * self.cell_size + self.cell_size // 2)
        arcade.draw_circle_filled(ball_x, ball_y, self.cell_size // 3, arcade.color.BLUE)

    def on_key_press(self, key, modifiers):
        """Move the ball with arrow keys."""
        if key == arcade.key.UP:
            self.move_ball("up")
        elif key == arcade.key.DOWN:
            self.move_ball("down")
        elif key == arcade.key.LEFT:
            self.move_ball("left")
        elif key == arcade.key.RIGHT:
            self.move_ball("right")


    # ===== New method to move the ball programmatically =====
    def move_ball(self, direction):
        """Move ball in ['up', 'down', 'left', 'right']"""
        new_r, new_c = self.ball_row, self.ball_col
        if direction == 'up':
            new_r -= 1
        elif direction == 'down':
            new_r += 1
        elif direction == 'left':
            new_c -= 1
        elif direction == 'right':
            new_c += 1


        # Check bounds and collisions
        if 0 <= new_r < self.rows and 0 <= new_c < self.cols:
            if self.maze[new_r, new_c] == 0:  # move only into empty space
                self.ball_row, self.ball_col = new_r, new_c
                self.ball_pos = (self.ball_col, self.ball_row)
                self.reveal_area(self.ball_row, self.ball_col)

# ===== Run the game =====
if __name__ == "__main__":
    from demo_engine.assets import random_maze as maz
    
    mat = maz.random_maze()
    maze = maz.expand_with_gaps(mat)
    window = MazeGame(maze)
    arcade.run()
