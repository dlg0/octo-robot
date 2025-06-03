import arcade
import math
from game.item_manager import ITEM_RADIUS, ITEM_TYPES
from game.player import PLAYER_RADIUS
from game.obstacle_manager import OBSTACLE_TYPES

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
        """Draw the player with enhanced visual design"""
        # Main body
        arcade.draw_circle_filled(self.player.x, self.player.y, PLAYER_RADIUS, arcade.color.PURPLE_HEART)
        
        # Outer ring for depth
        arcade.draw_circle_outline(self.player.x, self.player.y, PLAYER_RADIUS + 2, arcade.color.PURPLE, 2)
        
        # Eyes
        eye_offset_x = 8
        eye_offset_y = 8
        eye_size = 4
        pupil_size = 2
        
        # Left eye
        arcade.draw_circle_filled(self.player.x - eye_offset_x, self.player.y + eye_offset_y, eye_size, arcade.color.WHITE)
        arcade.draw_circle_filled(self.player.x - eye_offset_x, self.player.y + eye_offset_y, pupil_size, arcade.color.BLACK)
        
        # Right eye
        arcade.draw_circle_filled(self.player.x + eye_offset_x, self.player.y + eye_offset_y, eye_size, arcade.color.WHITE)
        arcade.draw_circle_filled(self.player.x + eye_offset_x, self.player.y + eye_offset_y, pupil_size, arcade.color.BLACK)
        
        # Antenna/details
        arcade.draw_line(self.player.x, self.player.y + PLAYER_RADIUS, 
                        self.player.x, self.player.y + PLAYER_RADIUS + 10, 
                        arcade.color.PURPLE, 3)
        arcade.draw_circle_filled(self.player.x, self.player.y + PLAYER_RADIUS + 12, 3, arcade.color.RED)

    def draw_items(self, camera_x=0, camera_y=0, screen_width=800, screen_height=600):
        """Draw items near the camera position"""
        # Calculate culling radius based on the larger screen dimension to ensure all visible items are fetched.
        # Add a small buffer just in case.
        culling_radius = max(screen_width, screen_height) * 0.75 # Ensure items up to the corners are included
        if culling_radius < 1000: # ensure a minimum culling distance
            culling_radius = 1000

        if hasattr(self.item_manager, 'get_active_items_near'):
            # Use optimized rendering for large worlds
            items = self.item_manager.get_active_items_near(camera_x, camera_y, culling_radius)
        else:
            # Fallback for compatibility
            items = self.item_manager.get_active_items()
        
        for item in items:
            item_props = ITEM_TYPES[item.type]
            color = item_props["color"]
            
            # Draw item with enhanced visuals based on type
            if item.type == "battery":
                self.draw_battery(item.x, item.y, color)
            elif item.type == "gear":
                self.draw_gear(item.x, item.y, color)
            elif item.type == "gem":
                self.draw_gem(item.x, item.y, color)
            elif item.type == "crystal":
                self.draw_crystal(item.x, item.y, color)
            elif item.type == "power_core":
                self.draw_power_core(item.x, item.y, color)
            else:
                # Default circular item
                arcade.draw_circle_filled(item.x, item.y, ITEM_RADIUS, color)
                arcade.draw_circle_outline(item.x, item.y, ITEM_RADIUS, arcade.color.WHITE, 2)

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
        """Draw obstacles near the camera position"""
        if not self.obstacle_manager:
            return
        
        # Calculate culling radius based on the larger screen dimension.
        culling_radius = max(screen_width, screen_height) * 0.75 # Ensure obstacles up to the corners are included
        if culling_radius < 1000: # ensure a minimum culling distance
            culling_radius = 1000
            
        obstacles = self.obstacle_manager.get_active_obstacles_near(camera_x, camera_y, culling_radius)
        
        for obstacle in obstacles:
            obstacle_props = OBSTACLE_TYPES[obstacle.type]
            color = obstacle_props["color"]
            
            if obstacle.type == "rock":
                self.draw_rock(obstacle.x, obstacle.y, obstacle.radius, color)
            elif obstacle.type == "tree":
                self.draw_tree(obstacle.x, obstacle.y, obstacle.radius, color)
            elif obstacle.type == "crystal_formation":
                self.draw_crystal_formation(obstacle.x, obstacle.y, obstacle.radius, color)
            elif obstacle.type == "metal_debris":
                self.draw_metal_debris(obstacle.x, obstacle.y, obstacle.radius, color)
            else:
                # Default circular obstacle
                arcade.draw_circle_filled(obstacle.x, obstacle.y, obstacle.radius, color)

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
        """Draw the user interface that adapts to screen size"""
        # Calculate UI position based on camera for fixed positioning
        ui_left = camera_x - screen_width / 2
        ui_right = camera_x + screen_width / 2
        ui_top = camera_y + screen_height / 2
        ui_bottom = camera_y - screen_height / 2
        
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