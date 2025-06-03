import arcade
import math
from game.item_manager import ITEM_RADIUS, ITEM_TYPES
from game.player import PLAYER_RADIUS
from game.obstacle_manager import OBSTACLE_TYPES
import logging
from game.config import MARGIN_X, MARGIN_Y

DEBUG_ENABLED = True  # Set to True to enable debug output for player drawing

class Renderer:
    def __init__(self, player, item_manager, obstacle_manager=None, background_manager=None):
        self.player = player
        self.item_manager = item_manager
        self.obstacle_manager = obstacle_manager
        self.background_manager = background_manager

    def draw_background(self, camera_x=0, camera_y=0, screen_width=800, screen_height=600):
        """Draw the infinite scrolling background"""
        if self.background_manager:
            self.background_manager.draw_background(camera_x, camera_y, screen_width, screen_height)
        else:
            # Fallback simple background with large buffer for fullscreen transitions
            buffer_size = max(500, max(screen_width, screen_height) * 0.5)
            view_left = camera_x - screen_width / 2
            view_right = camera_x + screen_width / 2
            view_bottom = camera_y - screen_height / 2
            view_top = camera_y + screen_height / 2
            
            # Sky background
            arcade.draw_rect_filled(
                arcade.LRBT(view_left - buffer_size, view_right + buffer_size, 
                           view_bottom - buffer_size, view_top + buffer_size),
                arcade.color.SKY_BLUE
            )
            # Simple ground
            arcade.draw_rect_filled(
                arcade.LRBT(view_left - buffer_size, view_right + buffer_size, 
                           view_bottom - buffer_size, view_bottom + 100),
                arcade.color.DARK_SPRING_GREEN
            )

    def draw_player(self):
        """Draw the player sprite."""
        if self.player:
            if DEBUG_ENABLED:
                print(f"[DEBUG] Player pos: ({self.player.center_x}, {self.player.center_y}), alpha: {getattr(self.player, 'alpha', 'N/A')}, scale: {getattr(self.player, 'scale', 'N/A')}, texture: {self.player.texture}, visible: {getattr(self.player, 'visible', 'N/A')}")
                # Draw a fallback circle at the player's position
                arcade.draw_circle_filled(self.player.center_x, self.player.center_y, PLAYER_RADIUS, arcade.color.RED)
            arcade.SpriteList([self.player]).draw()
        # The old detailed drawing logic (eyes, antenna) is now part of the Player sprite's texture
        # or could be added as sub-sprites to the Player if dynamic elements were needed.

    def draw_items(self, camera_x=0, camera_y=0, screen_width=800, screen_height=600):
        """Draw items using the ItemManager's SpriteList."""
        # The ItemManager now handles its own SpriteList.
        # We just need to tell it to draw.
        if self.item_manager and hasattr(self.item_manager, 'item_sprite_list'):
            self.item_manager.item_sprite_list.draw()
        else:
            # Fallback or error if item_manager or sprite_list is not set up as expected
            # This part can be enhanced with logging or more robust error handling
            pass

    def draw_battery(self, x, y, color):
        """Draw a battery collectible"""
        # Main body
        arcade.draw_rect_filled(arcade.LRBT(x - ITEM_RADIUS * 0.75, x + ITEM_RADIUS * 0.75, 
                                           y - ITEM_RADIUS, y + ITEM_RADIUS), color)
        # Top terminal
        arcade.draw_rect_filled(arcade.LRBT(x - ITEM_RADIUS * 0.25, x + ITEM_RADIUS * 0.25, 
                                           y + ITEM_RADIUS * 0.8, y + ITEM_RADIUS * 1.1), arcade.color.GRAY)
        # Outline
        arcade.draw_rect_outline(arcade.LRBT(x - ITEM_RADIUS * 0.75, x + ITEM_RADIUS * 0.75, 
                                            y - ITEM_RADIUS, y + ITEM_RADIUS), arcade.color.BLACK, 2)

    def draw_gear(self, x, y, color):
        """Draw a gear collectible"""
        # Main circle
        arcade.draw_circle_filled(x, y, ITEM_RADIUS, color)
        # Inner circle
        arcade.draw_circle_filled(x, y, ITEM_RADIUS * 0.6, arcade.color.GRAY)
        # Gear teeth (simplified)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            tooth_x = x + math.cos(rad) * ITEM_RADIUS * 1.2
            tooth_y = y + math.sin(rad) * ITEM_RADIUS * 1.2
            arcade.draw_circle_filled(tooth_x, tooth_y, 3, color)

    def draw_gem(self, x, y, color):
        """Draw a gem collectible"""
        # Diamond shape
        points = [
            (x, y + ITEM_RADIUS),      # top
            (x + ITEM_RADIUS * 0.7, y), # right
            (x, y - ITEM_RADIUS),      # bottom
            (x - ITEM_RADIUS * 0.7, y)  # left
        ]
        arcade.draw_polygon_filled(points, color)
        arcade.draw_polygon_outline(points, arcade.color.WHITE, 2)
        # Inner shine
        inner_points = [
            (x, y + ITEM_RADIUS * 0.5),
            (x + ITEM_RADIUS * 0.3, y),
            (x, y - ITEM_RADIUS * 0.5),
            (x - ITEM_RADIUS * 0.3, y)
        ]
        arcade.draw_polygon_filled(inner_points, arcade.color.WHITE)

    def draw_crystal(self, x, y, color):
        """Draw a crystal collectible"""
        # Hexagonal crystal
        points = []
        for i in range(6):
            angle = math.radians(i * 60)
            point_x = x + math.cos(angle) * ITEM_RADIUS
            point_y = y + math.sin(angle) * ITEM_RADIUS
            points.append((point_x, point_y))
        
        arcade.draw_polygon_filled(points, color)
        arcade.draw_polygon_outline(points, arcade.color.WHITE, 2)
        
        # Inner hexagon
        inner_points = []
        for i in range(6):
            angle = math.radians(i * 60)
            point_x = x + math.cos(angle) * ITEM_RADIUS * 0.5
            point_y = y + math.sin(angle) * ITEM_RADIUS * 0.5
            inner_points.append((point_x, point_y))
        arcade.draw_polygon_filled(inner_points, arcade.color.LIGHT_GRAY)

    def draw_power_core(self, x, y, color):
        """Draw a power core collectible"""
        # Main core
        arcade.draw_circle_filled(x, y, ITEM_RADIUS, color)
        # Energy rings
        for i in range(3):
            radius = ITEM_RADIUS + (i + 1) * 5
            arcade.draw_circle_outline(x, y, radius, color, 2)
        # Center
        arcade.draw_circle_filled(x, y, ITEM_RADIUS * 0.4, arcade.color.WHITE)

    def draw_obstacles(self, camera_x=0, camera_y=0, screen_width=800, screen_height=600):
        """Draw obstacles using the ObstacleManager's SpriteList."""
        # The ObstacleManager now handles its own SpriteList for drawing.
        if self.obstacle_manager and hasattr(self.obstacle_manager, 'obstacle_sprite_list'):
            self.obstacle_manager.obstacle_sprite_list.draw()
        else:
            # Fallback or error, e.g., if obstacle_manager is None or not set up with a sprite list
            pass # Consider logging an error or warning here if in debug mode

    def draw_rock(self, x, y, radius, color):
        """Draw a rock obstacle"""
        # Irregular rock shape
        points = []
        for i in range(8):
            angle = math.radians(i * 45)
            # Vary radius for irregular shape
            rock_radius = radius * (0.8 + 0.4 * math.sin(i))
            point_x = x + math.cos(angle) * rock_radius
            point_y = y + math.sin(angle) * rock_radius
            points.append((point_x, point_y))
        
        arcade.draw_polygon_filled(points, color)
        arcade.draw_polygon_outline(points, arcade.color.BLACK, 2)

    def draw_tree(self, x, y, radius, color):
        """Draw a tree obstacle"""
        # Trunk
        trunk_width = radius * 0.3
        trunk_height = radius * 1.5
        trunk_left = x - trunk_width/2
        trunk_right = x + trunk_width/2
        trunk_bottom = y - radius * 0.3 - trunk_height/2
        trunk_top = y - radius * 0.3 + trunk_height/2
        arcade.draw_rect_filled(arcade.LRBT(trunk_left, trunk_right, trunk_bottom, trunk_top), arcade.color.BROWN)
        
        # Foliage
        arcade.draw_circle_filled(x, y + radius * 0.2, radius, color)
        arcade.draw_circle_filled(x - radius * 0.3, y, radius * 0.7, color)
        arcade.draw_circle_filled(x + radius * 0.3, y, radius * 0.7, color)

    def draw_crystal_formation(self, x, y, radius, color):
        """Draw a crystal formation obstacle"""
        # Multiple crystals
        for i in range(5):
            angle = math.radians(i * 72)
            crystal_x = x + math.cos(angle) * radius * 0.5
            crystal_y = y + math.sin(angle) * radius * 0.5
            crystal_size = radius * (0.3 + 0.2 * (i % 2))
            
            # Crystal points
            points = [
                (crystal_x, crystal_y + crystal_size),
                (crystal_x + crystal_size * 0.5, crystal_y),
                (crystal_x, crystal_y - crystal_size * 0.3),
                (crystal_x - crystal_size * 0.5, crystal_y)
            ]
            arcade.draw_polygon_filled(points, color)

    def draw_metal_debris(self, x, y, radius, color):
        """Draw metal debris obstacle"""
        # Scattered metal pieces
        for i in range(4):
            angle = math.radians(i * 90 + 45)
            piece_x = x + math.cos(angle) * radius * 0.4
            piece_y = y + math.sin(angle) * radius * 0.4
            piece_size = radius * 0.3
            
            piece_left = piece_x - piece_size/2
            piece_right = piece_x + piece_size/2
            piece_bottom = piece_y - piece_size * 0.75
            piece_top = piece_y + piece_size * 0.75
            
            arcade.draw_rect_filled(arcade.LRBT(piece_left, piece_right, piece_bottom, piece_top), color)
            arcade.draw_rect_outline(arcade.LRBT(piece_left, piece_right, piece_bottom, piece_top), arcade.color.BLACK, 1)

    def draw_ui(self, score, total_value=None, camera_x=0, camera_y=0, screen_width=800, screen_height=600):
        """Draw the user interface that adapts to screen size, and debug rectangles if enabled."""
        ui_left = camera_x - screen_width / 2
        ui_right = camera_x + screen_width / 2
        ui_top = camera_y + screen_height / 2
        ui_bottom = camera_y - screen_height / 2
        
        # --- DEBUG: Draw camera viewport and margin box ---
        if DEBUG_ENABLED:
            # Draw camera viewport (blue)
            cam_x = camera_x
            cam_y = camera_y
            print(f"[DEBUG] Camera center: ({cam_x}, {cam_y})")
            print(f"[DEBUG] Viewport: left={ui_left}, right={ui_right}, top={ui_top}, bottom={ui_bottom}")
            # Draw and print margin box (yellow)
            margin_x = min(MARGIN_X, screen_width * 0.25)
            margin_y = min(MARGIN_Y, screen_height * 0.25)
            margin_left = ui_left + margin_x
            margin_right = ui_right - margin_x
            margin_top = ui_top - margin_y
            margin_bottom = ui_bottom + margin_y
            print(f"[DEBUG] Margin: left={margin_left}, right={margin_right}, top={margin_top}, bottom={margin_bottom}")
            viewport_rect = arcade.LRBT(ui_left, ui_right, ui_top, ui_bottom)
            arcade.draw_rect_outline(viewport_rect, arcade.color.BLUE, 3)
            margin_rect = arcade.LRBT(margin_left, margin_right, margin_top, margin_bottom)
            arcade.draw_rect_outline(margin_rect, arcade.color.YELLOW, 2)
        
        # Adaptive font sizes based on screen size
        base_size = min(screen_width, screen_height)
        title_font_size = max(16, int(base_size * 0.025))
        main_font_size = max(14, int(base_size * 0.02))
        small_font_size = max(12, int(base_size * 0.015))
        
        # Score display (top-left)
        arcade.draw_text(f"Items Collected: {score}", ui_left + 10, ui_top - 30, 
                        arcade.color.BLACK, title_font_size)
        
        # Value display if available
        if total_value is not None:
            arcade.draw_text(f"Total Value: {total_value}", ui_left + 10, ui_top - 60, 
                            arcade.color.BLACK, main_font_size)
        
        # Instructions (bottom-left)
        arcade.draw_text("Use WASD or Arrow Keys to move", ui_left + 10, ui_bottom + 40, 
                        arcade.color.BLACK, small_font_size)
        arcade.draw_text("Press R to reset", ui_left + 10, ui_bottom + 20, 
                        arcade.color.BLACK, small_font_size)
        arcade.draw_text("Press F for fullscreen", ui_left + 10, ui_bottom + 10, 
                        arcade.color.BLACK, small_font_size) 