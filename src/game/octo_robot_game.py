import arcade
from .player import Player
from .item_manager import ItemManager
from rendering.renderer import Renderer

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Octo-Robot"

class OctoRobotGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.player = Player()
        self.item_manager = ItemManager()
        self.renderer = Renderer(self.player, self.item_manager)
        self.score = 0
        self.set_update_rate(1/60)
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self):
        self.player.reset()
        self.item_manager.reset()
        self.score = 0

    def on_draw(self):
        self.clear()
        self.renderer.draw_background()
        self.renderer.draw_items()
        self.renderer.draw_player()
        self.renderer.draw_ui(self.score)

    def on_update(self, delta_time):
        self.player.update()
        collected = self.item_manager.check_collisions(self.player)
        self.score += collected

    def on_key_press(self, key, modifiers):
        self.player.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.player.on_key_release(key, modifiers) 