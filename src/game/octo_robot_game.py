import arcade
from arcade.camera import Camera2D
from arcade.types import LRBT
from .player import Player
from .item_manager import ItemManager
from .obstacle_manager import ObstacleManager
from .background_manager import BackgroundManager
from rendering.renderer import Renderer
import logging
import os
import time
from game.config import MARGIN_X, MARGIN_Y
from game.game_state import GameStateManager, GameState
from game.high_score_manager import HighScoreManager
from game.game_mode import GameMode

# --- Logging Configuration ---
DEBUG_ENABLED = False  # Set to True by the user for detailed debug logging

_log_level = logging.DEBUG if DEBUG_ENABLED else logging.WARNING
_log_format = '%(asctime)s - %(levelname)s - %(message)s'
_log_handlers: list[logging.Handler] = []

_formatter = logging.Formatter(_log_format)

# Clear any existing handlers from the root logger before calling basicConfig
# This prevents issues if the module is reloaded or logging is configured elsewhere.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    handler.close() # Close handlers before removing

if DEBUG_ENABLED:
    print("Octo-Robot: DEBUG MODE ENABLED. Logging to console and 'fullscreen_debug.log'.")
    _debug_log_path = os.path.join(os.getcwd(), 'fullscreen_debug.log')
    _file_handler = logging.FileHandler(_debug_log_path, mode='w')
    _file_handler.setFormatter(_formatter)
    _log_handlers.append(_file_handler)
else:
    print("Octo-Robot: DEBUG MODE DISABLED. Logging to console (WARNINGS and above only).")

_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(_formatter)
_log_handlers.append(_stream_handler)

logging.basicConfig(level=_log_level, handlers=_log_handlers)
# Note: basicConfig's format argument is ignored if handlers are provided and they have formatters.

logger = logging.getLogger(__name__) # Get logger for this module
# --- End of Logging Configuration ---

DEFAULT_SCREEN_WIDTH = 1400
DEFAULT_SCREEN_HEIGHT = 1200
SCREEN_TITLE = "Octo-Robot - Enhanced World"

class OctoRobotGame(arcade.Window):
    def __init__(self):
        super().__init__(DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        
        logger.info(f"=== GAME INITIALIZATION ===")
        logger.info(f"Initial window size: {self.width}x{self.height}")
        
        # Screen state tracking
        self.is_fullscreen = False
        self.windowed_size = (DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT)
        
        # Initialize game systems
        self.player = Player()
        print("Player class:", type(self.player), "module:", type(self.player).__module__)
        self.item_manager = ItemManager()
        self.obstacle_manager = ObstacleManager()
        self.background_manager = BackgroundManager()
        
        # Initialize game state and score management
        self.game_state_manager = GameStateManager()
        self.high_score_manager = HighScoreManager()
        
        # Initialize renderer with all managers
        self.renderer = Renderer(
            self.player, 
            self.item_manager, 
            self.obstacle_manager, 
            self.background_manager
        )
        
        # Game state
        self.score = 0
        self.total_value = 0
        self.camera = Camera2D()
        
        # Performance and rendering
        self.set_update_rate(1/60)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        
        logger.info(f"=== GAME INITIALIZATION COMPLETE ===")
        logger.info(f"Final window size: {self.width}x{self.height}")
        logger.info(f"Camera initialized at: {self.camera.position}")

    def setup(self):
        """Initialize the game state"""
        self.player.reset()
        self.item_manager.reset()
        self.obstacle_manager.reset()
        self.background_manager.reset()
        self.game_state_manager.set_state(GameState.PLAYING)
        
        # Legacy state (keep for compatibility during transition)
        self.score = 0
        self.total_value = 0
        self.camera.position = (0, 0)
        
        # Generate initial content around starting position
        self.update_world_generation()

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        import time
        start_time = time.time()
        
        logger.info(f"=== FULLSCREEN TOGGLE START ===")
        logger.info(f"Timestamp: {start_time}")
        logger.info(f"Current state - fullscreen: {self.is_fullscreen}, size: {self.width}x{self.height}")
        logger.info(f"Camera position: {self.camera.position}")
        logger.info(f"Player position: ({self.player.center_x}, {self.player.center_y})")
        
        pre_change_time = time.time()
        logger.info(f"Pre-change time: {pre_change_time - start_time:.4f}s")
        
        if self.is_fullscreen:
            # Switch to windowed mode
            logger.info(f"Switching to windowed mode. Current windowed_size target: {self.windowed_size}")
            logger.info(f"About to call set_fullscreen(False)")
            self.set_fullscreen(False)
            logger.info(f"set_fullscreen(False) completed. New size: {self.width}x{self.height}")
            # Update camera viewport to match new window size
            self.camera.viewport = self.rect
            self.is_fullscreen = False
        else:
            # Store current windowed size before going fullscreen
            self.windowed_size = (self.width, self.height)
            logger.info(f"Storing windowed size: {self.windowed_size}")
            # Switch to fullscreen mode
            logger.info("About to call set_fullscreen(True)")
            self.set_fullscreen(True)
            logger.info(f"set_fullscreen(True) completed. New size: {self.width}x{self.height}")
            self.is_fullscreen = True
            # Update camera viewport to match new window size
            self.camera.viewport = self.rect

        post_change_time = time.time()
        logger.info(f"Post-change time: {post_change_time - start_time:.4f}s")
        logger.info(f"After toggle - fullscreen: {self.is_fullscreen}, size: {self.width}x{self.height}")
        
        # Check window properties
        logger.info(f"Window properties - width: {self.width}, height: {self.height}")
        try:
            logger.info(f"Window fullscreen property: {self.fullscreen}")
        except:
            pass
        
        # Force IMMEDIATE and aggressive world generation for new screen size
        # This prevents unrendered areas when switching screen modes
        logger.info("Triggering IMMEDIATE world generation update")
        world_gen_start = time.time()
        
        # Generate multiple times to ensure coverage for larger screen
        for i in range(3):
            logger.info(f"World generation pass {i+1}/3")
            self.update_world_generation()
        
        world_gen_time = time.time() - world_gen_start
        logger.info(f"World generation took: {world_gen_time:.4f}s")
        
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"=== FULLSCREEN TOGGLE END - Total time: {total_time:.4f}s ===")
    
    def on_resize(self, width, height):
        """Handle window resize events"""
        import time
        resize_start = time.time()
        
        logger.info(f"=== RESIZE EVENT START ===")
        logger.info(f"Resize timestamp: {resize_start}")
        logger.info(f"New size requested: {width}x{height}")
        logger.info(f"Previous size: {self.width}x{self.height}")
        logger.info(f"Current fullscreen state: {self.is_fullscreen}")
        
        super().on_resize(width, height)
        
        resize_after_super = time.time()
        logger.info(f"super().on_resize() took: {resize_after_super - resize_start:.4f}s")
        logger.info(f"Size after super().on_resize(): {self.width}x{self.height}")
        
        # Update camera viewport to match new window size
        self.camera.viewport = self.rect
        
        # Explicitly update camera for new dimensions after resize
        logger.info(f"Camera position after explicit update (should be unchanged): {self.camera.position}")
        
        # Force world generation update for new screen size
        # This ensures all visible areas have content when window is resized
        logger.info("Triggering world generation from resize")
        world_gen_start = time.time()
        self.update_world_generation()
        world_gen_time = time.time() - world_gen_start
        logger.info(f"World generation from resize took: {world_gen_time:.4f}s")
        
        resize_total = time.time() - resize_start
        logger.info(f"=== RESIZE EVENT END - Total time: {resize_total:.4f}s ===")

    def get_screen_dimensions(self):
        """Get current screen dimensions"""
        dimensions = (self.width, self.height)
        logger.debug(f"Screen dimensions: {dimensions}")
        return dimensions

    def on_draw(self):
        """Render the game"""
        import time
        frame_start = time.time()
        DEBUG_ENABLED = False  # Set to True to print camera position for debugging
        
        logger.debug(f"=== DRAW FRAME START ===")
        logger.debug(f"Frame timestamp: {frame_start}")
        logger.debug(f"Screen size: {self.width}x{self.height}")
        logger.debug(f"Fullscreen state: {self.is_fullscreen}")
        
        # Clear the entire viewport - ensure we clear the full screen
        clear_start = time.time()
        self.clear()
        clear_time = time.time() - clear_start
        logger.debug(f"Clear took: {clear_time:.6f}s")
        
        # Get camera position for rendering
        camera_x, camera_y = self.camera.position
        screen_width, screen_height = self.get_screen_dimensions()
        if DEBUG_ENABLED:
            print(f"[DEBUG] Camera pos: ({camera_x}, {camera_y})")
        
        logger.debug(f"Camera position: ({camera_x}, {camera_y})")
        logger.debug(f"Viewport: {screen_width}x{screen_height}")
        
        # Use camera for world rendering
        camera_start = time.time()
        self.camera.use()
        camera_time = time.time() - camera_start
        logger.debug(f"Camera.use() took: {camera_time:.6f}s")
        
        # Draw in order: background -> obstacles -> items -> player
        bg_start = time.time()
        logger.debug("Drawing background")
        self.renderer.draw_background(camera_x, camera_y, screen_width, screen_height)
        bg_time = time.time() - bg_start
        logger.debug(f"Background draw took: {bg_time:.6f}s")
        
        obs_start = time.time()
        logger.debug("Drawing obstacles")
        self.renderer.draw_obstacles(camera_x, camera_y, screen_width, screen_height)
        obs_time = time.time() - obs_start
        logger.debug(f"Obstacles draw took: {obs_time:.6f}s")
        
        items_start = time.time()
        logger.debug("Drawing items")
        self.renderer.draw_items(camera_x, camera_y, screen_width, screen_height)
        items_time = time.time() - items_start
        logger.debug(f"Items draw took: {items_time:.6f}s")
        
        player_start = time.time()
        logger.debug("Drawing player")
        self.renderer.draw_player()
        player_time = time.time() - player_start
        logger.debug(f"Player draw took: {player_time:.6f}s")
        
        # Draw UI (it will handle its own positioning)
        ui_start = time.time()
        logger.debug("Drawing UI")
        self.renderer.draw_ui(self.game_state_manager, camera_x, camera_y, screen_width, screen_height, self.high_score_manager)
        ui_time = time.time() - ui_start
        logger.debug(f"UI draw took: {ui_time:.6f}s")
        
        frame_total = time.time() - frame_start
        logger.debug(f"=== DRAW FRAME END - Total: {frame_total:.6f}s ===")

    def on_update(self, delta_time):
        """Update game logic"""
        # Update game state time
        if self.game_state_manager.is_playing():
            self.game_state_manager.update_game_time(delta_time)
        
        # Update player with obstacle collision detection
        self.player.update(self.obstacle_manager)
        
        # Check item collections
        collected_result = self.item_manager.check_collisions(self.player)
        if isinstance(collected_result, tuple):
            collected_value, collected_items = collected_result
        else:
            # Fallback for backward compatibility
            collected_value = collected_result
            collected_items = []
        
        if collected_value > 0:
            # Process each collected item for color matching
            for item_info in collected_items:
                item_color = item_info["color_name"]
                item_value = item_info["value"]
                item_type = item_info["type"]
                
                print(f"[GAME] Collected {item_type} (color: {item_color}) - Player color: {self.player.current_color}")
                
                # Check if item color matches player color
                if item_color == self.player.current_color:
                    # Matching color: add points
                    self.game_state_manager.add_score(item_value)
                    print(f"[GAME] Color match! Adding {item_value} points")
                else:
                    # Wrong color: change player color and reset score
                    print(f"[GAME] Color mismatch! Changing player color from {self.player.current_color} to {item_color} and resetting score")
                    self.player.change_color(item_color)
                    self.game_state_manager.reset_score()
            
            # Check if player reached the goal
            if self.game_state_manager.score >= 100:
                self.game_state_manager.complete_game()
        
        # Update camera to follow player
        self.scroll_camera_to_player()
        
        # Generate world content around player
        self.update_world_generation()

    def update_world_generation(self):
        """Update procedural generation around the player"""
        logger.debug(f"=== WORLD GENERATION START ===")
        logger.debug(f"Player position: ({self.player.center_x}, {self.player.center_y})")
        logger.debug(f"Camera position: {self.camera.position}")
        
        # Generate items around player position
        logger.debug("Generating items...")
        self.item_manager.update_generation(self.player.center_x, self.player.center_y)
        
        # Generate obstacles around player position
        logger.debug("Generating obstacles...")
        self.obstacle_manager.update_generation(self.player.center_x, self.player.center_y)
        
        # Generate background around camera position
        camera_x, camera_y = self.camera.position
        screen_width, screen_height = self.get_screen_dimensions()
        logger.debug(f"Generating background for camera: ({camera_x}, {camera_y}), screen: {screen_width}x{screen_height}")
        self.background_manager.update_generation(camera_x, camera_y, screen_width, screen_height)
        
        logger.debug(f"=== WORLD GENERATION END ===")

    def scroll_camera_to_player(self):
        """Smooth camera following with margins (fixed for symmetric scrolling)"""
        screen_width, screen_height = self.get_screen_dimensions()
        
        # Apply mode-specific margin multiplier
        margin_multiplier = GameMode.get_margin_multiplier(self.game_state_manager.get_current_mode())
        margin_x = min(MARGIN_X * margin_multiplier, screen_width * 0.25)
        margin_y = min(MARGIN_Y * margin_multiplier, screen_height * 0.25)

        cam_x, cam_y = self.camera.position

        left_boundary = cam_x - (screen_width / 2) + margin_x
        right_boundary = cam_x + (screen_width / 2) - margin_x
        bottom_boundary = cam_y - (screen_height / 2) + margin_y
        top_boundary = cam_y + (screen_height / 2) - margin_y

        target_x, target_y = cam_x, cam_y

        if self.player.center_x < left_boundary:
            target_x = self.player.center_x - margin_x + (screen_width / 2)
        elif self.player.center_x > right_boundary:
            target_x = self.player.center_x + margin_x - (screen_width / 2)

        if self.player.center_y < bottom_boundary:
            target_y = self.player.center_y - margin_y + (screen_height / 2)
        elif self.player.center_y > top_boundary:
            target_y = self.player.center_y + margin_y - (screen_height / 2)

        # Smooth camera movement
        lerp_factor = 0.1
        new_x = cam_x + (target_x - cam_x) * lerp_factor
        new_y = cam_y + (target_y - cam_y) * lerp_factor

        self.camera.position = (new_x, new_y)

    def on_key_press(self, key, modifiers):
        """Handle key press events"""
        logger.debug(f"=== KEY PRESS EVENT ===")
        logger.debug(f"Key: {key}, Modifiers: {modifiers}")
        logger.debug(f"Current window state - fullscreen: {self.is_fullscreen}, size: {self.width}x{self.height}")
        
        # Handle mode selection
        if key == arcade.key.M:
            self.game_state_manager.show_mode_selection()
        elif self.game_state_manager.is_mode_selection():
            if key == arcade.key.KEY_1:
                self.game_state_manager.set_game_mode(GameMode.FLETCHY)
                self.game_state_manager.start_playing()
            elif key == arcade.key.KEY_2:
                self.game_state_manager.set_game_mode(GameMode.SPENCY)
                self.game_state_manager.start_playing()
            elif key == arcade.key.KEY_3:
                self.game_state_manager.set_game_mode(GameMode.CHARLIE)
                self.game_state_manager.start_playing()
            elif key == arcade.key.ESCAPE:
                self.game_state_manager.start_playing()
            return

        # Handle different game states
        if self.game_state_manager.is_playing():
            self.player.on_key_press(key, modifiers)
            
            # Reset game with R key
            if key == arcade.key.R:
                logger.info("Reset key pressed - triggering game reset")
                self.setup()
            
            # Toggle fullscreen with F key
            elif key == arcade.key.F:
                logger.info(f"FULLSCREEN KEY PRESSED - Current state: {self.is_fullscreen}")
                self.toggle_fullscreen()
            
            # View high scores with H key
            elif key == arcade.key.H:
                self.game_state_manager.show_high_scores()
        
        elif self.game_state_manager.is_game_over():
            if key == arcade.key.ENTER:
                # Check if it's a high score
                if self.high_score_manager.is_high_score(self.game_state_manager.final_score, self.game_state_manager.final_time):
                    self.game_state_manager.start_name_entry()
                else:
                    self.setup()  # Restart game
            elif key == arcade.key.R:
                self.setup()  # Restart game
            elif key == arcade.key.H:
                self.game_state_manager.show_high_scores()
        
        elif self.game_state_manager.is_name_entry():
            if key == arcade.key.ENTER:
                # Save the high score and show high scores
                name = self.game_state_manager.entered_name if self.game_state_manager.entered_name else "Anonymous"
                self.high_score_manager.add_score(name, self.game_state_manager.final_score, self.game_state_manager.final_time)
                self.game_state_manager.show_high_scores()
            elif key == arcade.key.BACKSPACE:
                # Remove last character
                if self.game_state_manager.entered_name:
                    self.game_state_manager.entered_name = self.game_state_manager.entered_name[:-1]
            else:
                # Add character to name (limit to reasonable characters and length)
                if len(self.game_state_manager.entered_name) < 15:
                    char = None
                    if 32 <= key <= 126:  # Printable ASCII characters
                        char = chr(key)
                    elif key == arcade.key.SPACE:
                        char = ' '
                    
                    if char and char.isprintable():
                        # Handle shift for uppercase
                        if modifiers & arcade.key.MOD_SHIFT:
                            char = char.upper()
                        else:
                            char = char.lower()
                        self.game_state_manager.entered_name += char
        
        elif self.game_state_manager.is_high_scores():
            if key == arcade.key.R:
                self.setup()  # Restart game
            elif key == arcade.key.ESCAPE:
                self.game_state_manager.start_playing()  # Return to game
        
        logger.debug(f"=== KEY PRESS EVENT END ===")

    def on_key_release(self, key, modifiers):
        """Handle key release events"""
        self.player.on_key_release(key, modifiers) 