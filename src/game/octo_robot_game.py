import arcade
from arcade.camera import Camera2D
from .player import Player
from .item_manager import ItemManager
from rendering.renderer import Renderer

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Octo-Robot"
MARGIN_X = 200  # Margin from left/right edge
MARGIN_Y = 150  # Margin from top/bottom edge

class OctoRobotGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.player = Player()
        self.item_manager = ItemManager()
        self.renderer = Renderer(self.player, self.item_manager)
        self.score = 0
        self.camera = Camera2D()
        self.set_update_rate(1/60)
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self):
        self.player.reset()
        self.item_manager.reset()
        self.score = 0
        self.camera.position = (0, 0)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.renderer.draw_background()
        self.renderer.draw_items()
        self.renderer.draw_player()
        self.renderer.draw_ui(self.score)

    def on_update(self, delta_time):
        self.player.update()
        collected = self.item_manager.check_collisions(self.player)
        self.score += collected
        self.scroll_camera_to_player()

    def scroll_camera_to_player(self):
        # Calculate the visible area based on camera's center position
        # Camera position is the center of what we're looking at
        left_edge = self.camera.position[0] - SCREEN_WIDTH / 2
        right_edge = self.camera.position[0] + SCREEN_WIDTH / 2
        bottom_edge = self.camera.position[1] - SCREEN_HEIGHT / 2
        top_edge = self.camera.position[1] + SCREEN_HEIGHT / 2
        
        # Calculate boundaries with margins
        left_boundary = left_edge + MARGIN_X
        right_boundary = right_edge - MARGIN_X
        bottom_boundary = bottom_edge + MARGIN_Y
        top_boundary = top_edge - MARGIN_Y

        target_x = self.camera.position[0]
        target_y = self.camera.position[1]

        # Check if player is outside margins and adjust camera
        if self.player.x < left_boundary:
            target_x = self.player.x - MARGIN_X + SCREEN_WIDTH / 2
        elif self.player.x > right_boundary:
            target_x = self.player.x + MARGIN_X - SCREEN_WIDTH / 2

        if self.player.y < bottom_boundary:
            target_y = self.player.y - MARGIN_Y + SCREEN_HEIGHT / 2
        elif self.player.y > top_boundary:
            target_y = self.player.y + MARGIN_Y - SCREEN_HEIGHT / 2

        self.camera.position = (target_x, target_y)

    def on_key_press(self, key, modifiers):
        self.player.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.player.on_key_release(key, modifiers) 