import arcade
import math
from game.item_manager import ITEM_RADIUS, ITEM_TYPES
from game.player import PLAYER_RADIUS
from game.obstacle_manager import OBSTACLE_TYPES
import logging
from game.config import MARGIN_X, MARGIN_Y
from game.game_mode import GameMode

DEBUG_ENABLED = False  # Set to True to enable debug output for player drawing

class Renderer:
    def __init__(self, player, item_manager, obstacle_manager=None, background_manager=None):
        self.player = player
        self.item_manager = item_manager
        self.obstacle_manager = obstacle_manager
        self.background_manager = background_manager
        
        # Cache for Text objects to improve performance
        self.text_cache = {}
        self.last_screen_size = (0, 0)  # Track screen size changes to update text

    def _get_text_object(self, text, font_size, color=arcade.color.BLACK, anchor_x="left"):
        """Get a cached Text object or create a new one for better performance"""
        cache_key = (text, font_size, color, anchor_x)
        if cache_key not in self.text_cache:
            self.text_cache[cache_key] = arcade.Text(
                text, 0, 0, color, font_size, anchor_x=anchor_x
            )
        return self.text_cache[cache_key]

    def _clear_text_cache(self):
        """Clear the text cache when screen size changes"""
        self.text_cache.clear()

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
            
            # Always draw a fallback circle at the player's position for visibility
            # Use the player's current color if available
            if hasattr(self.player, 'color_tuple'):
                player_color = self.player.color_tuple
            else:
                player_color = arcade.color.RED  # Default fallback
            arcade.draw_circle_filled(self.player.center_x, self.player.center_y, PLAYER_RADIUS, player_color)
            
            # Also try to draw the sprite (this should be the main rendering method)
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
            
            # Draw red boundaries around colliding obstacles
            if hasattr(self.obstacle_manager, 'get_colliding_obstacles'):
                colliding_obstacles = self.obstacle_manager.get_colliding_obstacles()
                for obstacle in colliding_obstacles:
                    # Draw a thick red circle outline around the colliding obstacle
                    if hasattr(obstacle, 'radius'):
                        # Draw multiple circles for a thicker appearance
                        for width in range(1, 4):
                            arcade.draw_circle_outline(
                                obstacle.center_x, 
                                obstacle.center_y, 
                                obstacle.radius + width, 
                                arcade.color.RED, 
                                border_width=1
                            )
                    else:
                        # Fallback: draw around the sprite's bounds
                        arcade.draw_rectangle_outline(
                            obstacle.center_x,
                            obstacle.center_y,
                            obstacle.width + 6,
                            obstacle.height + 6,
                            arcade.color.RED,
                            border_width=3
                        )
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

    def draw_playing_ui(self, game_state, ui_left, ui_right, ui_top, ui_bottom, title_font_size, main_font_size, small_font_size):
        """Draw UI elements during gameplay"""
        screen_width = ui_right - ui_left  # Calculate screen width from UI bounds
        
        # Check if screen size changed and clear cache if needed
        current_size = (screen_width, ui_top - ui_bottom)
        if current_size != self.last_screen_size:
            self._clear_text_cache()
            self.last_screen_size = current_size
        
        # Score display (top-left) - moved lower from top edge
        score_text = self._get_text_object(f"Score: {game_state.score}/100", title_font_size, arcade.color.BLACK)
        score_text.x = ui_left + 20
        score_text.y = ui_top - 50
        score_text.draw()
        
        # Timer display (top-right) - moved lower and less far right
        time_text_obj = self._get_text_object(f"Time: {game_state.game_time:.1f}s", title_font_size, arcade.color.BLACK)
        time_text_obj.x = ui_right - 180
        time_text_obj.y = ui_top - 50
        time_text_obj.draw()

        # Current mode display (top-center)
        mode_text = self._get_text_object(f"Mode: {game_state.get_current_mode().value.title()}", main_font_size, arcade.color.BLACK, anchor_x="center")
        mode_text.x = ui_left + screen_width // 2
        mode_text.y = ui_top - 50
        mode_text.draw()
        
        # Progress bar (top-center, below score/timer)
        progress_bar_width = min(300, screen_width * 0.4)
        progress_bar_height = 20
        progress_bar_x = ui_left + screen_width // 2 - progress_bar_width // 2
        progress_bar_y = ui_top - 90
        
        # Progress bar background (gray border)
        progress_bg_rect = arcade.LRBT(
            progress_bar_x - 2, progress_bar_x + progress_bar_width + 2,
            progress_bar_y - 2, progress_bar_y + progress_bar_height + 2
        )
        arcade.draw_rect_filled(progress_bg_rect, arcade.color.DARK_GRAY)
        
        # Progress bar inner background (white)
        progress_inner_rect = arcade.LRBT(
            progress_bar_x, progress_bar_x + progress_bar_width,
            progress_bar_y, progress_bar_y + progress_bar_height
        )
        arcade.draw_rect_filled(progress_inner_rect, arcade.color.WHITE)
        
        # Progress bar fill
        progress_percentage = min(game_state.score / 100.0, 1.0)
        progress_fill_width = progress_bar_width * progress_percentage
        
        if progress_fill_width > 0:
            # Color changes based on progress
            if progress_percentage < 0.3:
                fill_color = arcade.color.RED
            elif progress_percentage < 0.6:
                fill_color = arcade.color.ORANGE
            elif progress_percentage < 0.9:
                fill_color = arcade.color.YELLOW
            else:
                fill_color = arcade.color.GREEN
            
            progress_fill_rect = arcade.LRBT(
                progress_bar_x, progress_bar_x + progress_fill_width,
                progress_bar_y, progress_bar_y + progress_bar_height
            )
            arcade.draw_rect_filled(progress_fill_rect, fill_color)
        
        # Progress percentage text (centered on progress bar)
        progress_text = self._get_text_object(f"{int(progress_percentage * 100)}%", main_font_size, arcade.color.BLACK, anchor_x="center")
        progress_text.x = progress_bar_x + progress_bar_width // 2
        progress_text.y = progress_bar_y + progress_bar_height // 2 - 6  # Center vertically
        progress_text.draw()
        
        # Current player color (top-center, below progress bar)
        if hasattr(self.player, 'current_color'):
            color_text = self._get_text_object(f"Color: {self.player.current_color.title()}", main_font_size, arcade.color.BLACK, anchor_x="center")
            color_text.x = ui_left + screen_width//2
            color_text.y = ui_top - 100
            color_text.draw()
        
        # Goal explanation (top-left, below score)
        goal_text = self._get_text_object("Collect dots matching your color!", main_font_size, arcade.color.DARK_BLUE)
        goal_text.x = ui_left + 10
        goal_text.y = ui_top - 120
        goal_text.draw()
        
        wrong_color_text = self._get_text_object("Wrong color = color change + score reset", small_font_size, arcade.color.DARK_RED)
        wrong_color_text.x = ui_left + 10
        wrong_color_text.y = ui_top - 140
        wrong_color_text.draw()
        
        # Instructions (bottom-left)
        instructions = [
            ("Use WASD or Arrow Keys to move", ui_bottom + 60),
            ("Press R to reset", ui_bottom + 40),
            ("Press F for fullscreen", ui_bottom + 20),
            ("Press H to view high scores", ui_bottom + 10)
        ]
        
        for instruction_text, y_pos in instructions:
            text_obj = self._get_text_object(instruction_text, small_font_size, arcade.color.BLACK)
            text_obj.x = ui_left + 10
            text_obj.y = y_pos
            text_obj.draw()
    
    def draw_game_over_ui(self, game_state, ui_left, ui_right, ui_top, ui_bottom, title_font_size, large_font_size, main_font_size, small_font_size, high_score_manager):
        """Draw game over screen"""
        center_x = (ui_left + ui_right) / 2
        center_y = (ui_top + ui_bottom) / 2
        
        # Semi-transparent overlay
        overlay_rect = arcade.LRBT(ui_left, ui_right, ui_bottom, ui_top)
        arcade.draw_rect_filled(overlay_rect, (0, 0, 0, 128))
        
        # Congratulations message
        arcade.draw_text("GOAL ACHIEVED!", center_x, center_y + 100, 
                        arcade.color.GOLD, title_font_size, anchor_x="center")
        
        # Final score and time
        arcade.draw_text(f"Final Score: {game_state.final_score}", center_x, center_y + 60, 
                        arcade.color.WHITE, large_font_size, anchor_x="center")
        arcade.draw_text(f"Time: {game_state.final_time:.2f} seconds", center_x, center_y + 30, 
                        arcade.color.WHITE, large_font_size, anchor_x="center")
        
        # Check if it's a high score
        is_high_score = False
        if high_score_manager:
            is_high_score = high_score_manager.is_high_score(game_state.final_score, game_state.final_time)
        
        if is_high_score:
            arcade.draw_text("NEW HIGH SCORE!", center_x, center_y - 10, 
                            arcade.color.YELLOW, large_font_size, anchor_x="center")
            arcade.draw_text("Press ENTER to enter your name", center_x, center_y - 40, 
                            arcade.color.WHITE, main_font_size, anchor_x="center")
        else:
            arcade.draw_text("Press ENTER to continue", center_x, center_y - 10, 
                            arcade.color.WHITE, main_font_size, anchor_x="center")
        
        # Instructions
        arcade.draw_text("Press R to play again", center_x, center_y - 80, 
                        arcade.color.LIGHT_GRAY, small_font_size, anchor_x="center")
        arcade.draw_text("Press H to view high scores", center_x, center_y - 100, 
                        arcade.color.LIGHT_GRAY, small_font_size, anchor_x="center")
    
    def draw_name_entry_ui(self, game_state, ui_left, ui_right, ui_top, ui_bottom, title_font_size, large_font_size, main_font_size, small_font_size):
        """Draw name entry screen"""
        center_x = (ui_left + ui_right) / 2
        center_y = (ui_top + ui_bottom) / 2
        
        # Semi-transparent overlay
        overlay_rect = arcade.LRBT(ui_left, ui_right, ui_bottom, ui_top)
        arcade.draw_rect_filled(overlay_rect, (0, 0, 0, 128))
        
        # Title
        arcade.draw_text("HIGH SCORE!", center_x, center_y + 100, 
                        arcade.color.GOLD, title_font_size, anchor_x="center")
        
        # Score display
        arcade.draw_text(f"Score: {game_state.final_score} - Time: {game_state.final_time:.2f}s", 
                        center_x, center_y + 60, arcade.color.WHITE, large_font_size, anchor_x="center")
        
        # Name entry prompt
        arcade.draw_text("Enter your name:", center_x, center_y + 20, 
                        arcade.color.WHITE, main_font_size, anchor_x="center")
        
        # Name input box
        name_box_width = 300
        name_box_height = 40
        name_box_left = center_x - name_box_width / 2
        name_box_right = center_x + name_box_width / 2
        name_box_bottom = center_y - 20
        name_box_top = center_y + 20
        
        # Draw input box
        name_box_rect = arcade.LRBT(name_box_left, name_box_right, name_box_bottom, name_box_top)
        arcade.draw_rect_filled(name_box_rect, arcade.color.WHITE)
        arcade.draw_rect_outline(name_box_rect, arcade.color.BLACK, 2)
        
        # Draw entered name
        display_name = game_state.entered_name
        if len(display_name) == 0:
            display_name = "Anonymous"
        
        arcade.draw_text(display_name, center_x, center_y, 
                        arcade.color.BLACK, main_font_size, anchor_x="center")
        
        # Instructions
        arcade.draw_text("Type your name and press ENTER", center_x, center_y - 60, 
                        arcade.color.WHITE, small_font_size, anchor_x="center")
        arcade.draw_text("Press BACKSPACE to delete", center_x, center_y - 80, 
                        arcade.color.LIGHT_GRAY, small_font_size, anchor_x="center")
    
    def draw_high_scores_ui(self, game_state, ui_left, ui_right, ui_top, ui_bottom, title_font_size, large_font_size, main_font_size, small_font_size, high_score_manager):
        """Draw high scores screen"""
        center_x = (ui_left + ui_right) / 2
        center_y = (ui_top + ui_bottom) / 2
        
        # Semi-transparent overlay
        overlay_rect = arcade.LRBT(ui_left, ui_right, ui_bottom, ui_top)
        arcade.draw_rect_filled(overlay_rect, (0, 0, 0, 128))
        
        # Title
        arcade.draw_text("HIGH SCORES", center_x, center_y + 150, 
                        arcade.color.GOLD, title_font_size, anchor_x="center")
        
        # High scores list
        if high_score_manager:
            scores = high_score_manager.get_top_scores(10)
            if scores:
                start_y = center_y + 100
                for i, score_entry in enumerate(scores):
                    y_pos = start_y - (i * 25)
                    
                    # Highlight the new score if it exists
                    color = arcade.color.WHITE
                    if (hasattr(game_state, 'final_score') and hasattr(game_state, 'final_time') and
                        score_entry['score'] == game_state.final_score and 
                        abs(score_entry['time'] - game_state.final_time) < 0.01):
                        color = arcade.color.YELLOW
                    
                    score_text = f"{i+1:2d}. {score_entry['name']:<15} {score_entry['score']:3d} pts  {score_entry['time']:6.2f}s"
                    arcade.draw_text(score_text, center_x, y_pos, color, main_font_size, anchor_x="center")
            else:
                arcade.draw_text("No high scores yet!", center_x, center_y + 50, 
                                arcade.color.WHITE, main_font_size, anchor_x="center")
        
        # Instructions
        arcade.draw_text("Press R to play again", center_x, center_y - 150, 
                        arcade.color.WHITE, small_font_size, anchor_x="center")
        arcade.draw_text("Press ESC to return to game", center_x, center_y - 170, 
                        arcade.color.LIGHT_GRAY, small_font_size, anchor_x="center")

    def draw_mode_selection_ui(self, game_state, ui_left, ui_right, ui_top, ui_bottom, title_font_size, large_font_size, main_font_size, small_font_size):
        """Draw mode selection screen"""
        center_x = (ui_left + ui_right) / 2
        center_y = (ui_top + ui_bottom) / 2
        
        # Semi-transparent overlay
        overlay_rect = arcade.LRBT(ui_left, ui_right, ui_bottom, ui_top)
        arcade.draw_rect_filled(overlay_rect, (0, 0, 0, 128))
        
        # Title
        arcade.draw_text("SELECT GAME MODE", center_x, center_y + 150, 
                        arcade.color.GOLD, title_font_size, anchor_x="center")
        
        # Mode options
        modes = [
            ("Fletchy Mode (Easy)", GameMode.FLETCHY),
            ("Spency Mode (Normal)", GameMode.SPENCY),
            ("Charlie Mode (Hard)", GameMode.CHARLIE)
        ]
        
        start_y = center_y + 100
        for i, (mode_name, mode) in enumerate(modes):
            y_pos = start_y - (i * 50)
            
            # Highlight current mode
            color = arcade.color.YELLOW if mode == game_state.get_current_mode() else arcade.color.WHITE
            
            # Draw mode name
            arcade.draw_text(mode_name, center_x, y_pos, color, large_font_size, anchor_x="center")
            
            # Draw mode description
            if mode == GameMode.FLETCHY:
                desc = "Half the margin - easier gameplay"
            elif mode == GameMode.SPENCY:
                desc = "Default margin - balanced gameplay"
            else:  # Charlie mode
                desc = "Double the margin - challenging gameplay"
            
            arcade.draw_text(desc, center_x, y_pos - 25, arcade.color.LIGHT_GRAY, small_font_size, anchor_x="center")
        
        # Instructions
        arcade.draw_text("Press 1-3 to select mode", center_x, center_y - 150, 
                        arcade.color.WHITE, small_font_size, anchor_x="center")
        arcade.draw_text("Press ESC to return to game", center_x, center_y - 170, 
                        arcade.color.LIGHT_GRAY, small_font_size, anchor_x="center")

    def draw_ui(self, game_state=None, camera_x=0, camera_y=0, screen_width=800, screen_height=600, high_score_manager=None):
        """Draw the user interface that adapts to screen size and game state."""
        ui_left = camera_x - screen_width / 2
        ui_right = camera_x + screen_width / 2
        ui_top = camera_y + screen_height / 2
        ui_bottom = camera_y - screen_height / 2
        
        # Adaptive font sizes based on screen size
        base_size = min(screen_width, screen_height)
        title_font_size = max(20, int(base_size * 0.035))
        large_font_size = max(18, int(base_size * 0.03))
        main_font_size = max(14, int(base_size * 0.02))
        small_font_size = max(12, int(base_size * 0.015))
        
        if game_state is None:
            # Fallback to old UI if no game state provided
            arcade.draw_text("No game state provided", ui_left + 10, ui_top - 30, 
                            arcade.color.RED, main_font_size)
            return
        
        # Draw different UI based on game state
        if game_state.is_playing():
            self.draw_playing_ui(game_state, ui_left, ui_right, ui_top, ui_bottom, 
                               title_font_size, main_font_size, small_font_size)
        elif game_state.is_game_over():
            self.draw_game_over_ui(game_state, ui_left, ui_right, ui_top, ui_bottom, 
                                 title_font_size, large_font_size, main_font_size, small_font_size, high_score_manager)
        elif game_state.is_name_entry():
            self.draw_name_entry_ui(game_state, ui_left, ui_right, ui_top, ui_bottom, 
                                   title_font_size, large_font_size, main_font_size, small_font_size)
        elif game_state.is_high_scores():
            self.draw_high_scores_ui(game_state, ui_left, ui_right, ui_top, ui_bottom, 
                                   title_font_size, large_font_size, main_font_size, small_font_size, high_score_manager)
        elif game_state.is_mode_selection():
            self.draw_mode_selection_ui(game_state, ui_left, ui_right, ui_top, ui_bottom,
                                      title_font_size, large_font_size, main_font_size, small_font_size) 