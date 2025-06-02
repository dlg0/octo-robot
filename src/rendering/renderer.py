import arcade
from game.item_manager import ITEM_RADIUS, ITEM_COLORS
from game.player import PLAYER_RADIUS

class Renderer:
    def __init__(self, player, item_manager):
        self.player = player
        self.item_manager = item_manager

    def draw_background(self):
        # Draw sky background
        arcade.draw_rect_filled(arcade.LRBT(0, 800, 0, 600), arcade.color.SKY_BLUE)
        # Simple ground
        arcade.draw_rect_filled(arcade.LRBT(0, 800, 0, 100), arcade.color.DARK_SPRING_GREEN)

    def draw_player(self):
        arcade.draw_circle_filled(self.player.x, self.player.y, PLAYER_RADIUS, arcade.color.PURPLE_HEART)
        # Eyes for fun
        arcade.draw_circle_filled(self.player.x - 8, self.player.y + 8, 4, arcade.color.WHITE)
        arcade.draw_circle_filled(self.player.x + 8, self.player.y + 8, 4, arcade.color.WHITE)
        arcade.draw_circle_filled(self.player.x - 8, self.player.y + 8, 2, arcade.color.BLACK)
        arcade.draw_circle_filled(self.player.x + 8, self.player.y + 8, 2, arcade.color.BLACK)

    def draw_items(self):
        for item in self.item_manager.get_active_items():
            color = ITEM_COLORS[item.type]
            arcade.draw_circle_filled(item.x, item.y, ITEM_RADIUS, color)

    def draw_ui(self, score):
        arcade.draw_text(f"Items Collected: {score}", 10, 570, arcade.color.BLACK, 20) 