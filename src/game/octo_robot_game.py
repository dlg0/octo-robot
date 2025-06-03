import arcade
from arcade.camera import Camera2D
from arcade.types import LRBT
from .player import Player
from .item_manager import ItemManager
from .obstacle_manager import ObstacleManager
from .background_manager import BackgroundManager
from .game_state import GameStateManager, GameState
from .high_score_manager import HighScoreManager
from rendering.renderer import Renderer
import logging
import os
import time
from game.config import MARGIN_X, MARGIN_Y
import math

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

DEFAULT_SCREEN_WIDTH = 800
DEFAULT_SCREEN_HEIGHT = 600
SCREEN_TITLE = "Octo-Robot - Enhanced World"

# Fullscreen constants
FULLSCREEN_WIDTH = 1920
FULLSCREEN_HEIGHT = 1080

class OctoRobotGame(arcade.Window):
    def __init__(self):
        super().__init__(DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        
        logger.info(f"=== GAME INITIALIZATION ===")
        logger.info(f"Initial window size: {self.width}x{self.height}")
        
        # Screen state tracking
        self.is_fullscreen = False
        self.windowed_size = (DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT)
        
        # Logical screen dimensions - this is what the game thinks the screen size is
        # This can be different from actual window size to handle fullscreen scaling
        self.logical_width = DEFAULT_SCREEN_WIDTH
        self.logical_height = DEFAULT_SCREEN_HEIGHT
        
        # Initialize game systems
        self.player = Player()
        print("Player class:", type(self.player), "module:", type(self.player).__module__)
        self.item_manager = ItemManager()
        self.obstacle_manager = ObstacleManager()
        self.background_manager = BackgroundManager()
        
        # Initialize new game systems
        self.game_state = GameStateManager()
        self.high_score_manager = HighScoreManager()
        
        # Initialize renderer with all managers
        self.renderer = Renderer(
            self.player, 
            self.item_manager, 
            self.obstacle_manager, 
            self.background_manager
        )
        
        # Legacy game state (keeping for compatibility with old UI calls)
        self.score = 0
        self.total_value = 0
        self.camera = Camera2D()
        
        # Store original window dimensions for projection scaling
        self.original_width = DEFAULT_SCREEN_WIDTH
        self.original_height = DEFAULT_SCREEN_HEIGHT
        
        # Performance and rendering
        self.set_update_rate(1/60)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        
        logger.info(f"=== GAME INITIALIZATION COMPLETE ===")
        logger.info(f"Final window size: {self.width}x{self.height}")
        logger.info(f"Logical screen size: {self.logical_width}x{self.logical_height}")
        logger.info(f"Camera initialized at: {self.camera.position}")

    def setup(self):
        """Initialize the game state"""
        self.player.reset()
        self.item_manager.reset()
        self.obstacle_manager.reset()
        self.background_manager.reset()
        self.game_state.reset_game()
        
        # Legacy compatibility
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
        logger.info(f"Current logical size: {self.logical_width}x{self.logical_height}")
        logger.info(f"Camera position: {self.camera.position}")
        logger.info(f"Player position: ({self.player.center_x}, {self.player.center_y})")
        
        pre_change_time = time.time()
        logger.info(f"Pre-change time: {pre_change_time - start_time:.4f}s")
        
        if self.is_fullscreen:
            # Switch to windowed mode
            logger.info("Switching to windowed mode")
            self.set_fullscreen(False)
            self.set_size(self.original_width, self.original_height)
            self.is_fullscreen = False
            
            # Reset logical dimensions to original windowed size
            self.logical_width = self.original_width
            self.logical_height = self.original_height
            
            # Reset camera zoom to 1.0
            self.camera.zoom = 1.0
            
            logger.info(f"Reset logical dimensions to: {self.logical_width}x{self.logical_height}")
            
        else:
            # Switch to fullscreen mode
            logger.info("Switching to fullscreen mode")
            self.set_fullscreen(True)
            self.is_fullscreen = True
            
            # Update logical dimensions to match actual fullscreen size
            # This makes the game think the screen is actually bigger
            self.logical_width = self.width
            self.logical_height = self.height
            
            # Keep camera zoom at 1.0 - no need for zoom tricks
            self.camera.zoom = 1.0
            
            logger.info(f"Updated logical dimensions to: {self.logical_width}x{self.logical_height}")
            logger.info(f"Game now thinks screen is {self.logical_width}x{self.logical_height} instead of {self.original_width}x{self.original_height}")
        
        # Update camera viewport to match new window size
        self.camera.viewport = self.rect
        logger.info(f"Updated camera viewport to: {self.camera.viewport}")
        
        post_change_time = time.time()
        logger.info(f"Screen change took: {post_change_time - pre_change_time:.4f}s")
        logger.info(f"New state - fullscreen: {self.is_fullscreen}, size: {self.width}x{self.height}")
        logger.info(f"New logical size: {self.logical_width}x{self.logical_height}")
        logger.info(f"Camera position after change: {self.camera.position}")
        
        # Force world generation update for new screen size
        logger.info("Triggering world generation from fullscreen toggle")
        world_gen_start = time.time()
        self.update_world_generation()
        world_gen_time = time.time() - world_gen_start
        logger.info(f"World generation took: {world_gen_time:.4f}s")
        
        total_time = time.time() - start_time
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
        """Get current logical screen dimensions (what the game thinks the screen size is)"""
        dimensions = (self.logical_width, self.logical_height)
        logger.debug(f"Logical screen dimensions: {dimensions} (actual window: {self.width}x{self.height})")
        return dimensions

    def on_draw(self):
        """Render the game"""
        import time
        frame_start = time.time()
        DEBUG_ENABLED = False  # Set to False to reduce debug spam
        
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
        
        # Draw UI with new game state system
        ui_start = time.time()
        logger.debug("Drawing UI")
        self.renderer.draw_ui(
            game_state=self.game_state,
            camera_x=camera_x, 
            camera_y=camera_y, 
            screen_width=screen_width, 
            screen_height=screen_height,
            high_score_manager=self.high_score_manager
        )
        ui_time = time.time() - ui_start
        logger.debug(f"UI draw took: {ui_time:.6f}s")
        
        frame_total = time.time() - frame_start
        logger.debug(f"=== DRAW FRAME END - Total: {frame_total:.6f}s ===")

    def on_update(self, delta_time):
        """Update game logic"""
        # Update game timer
        self.game_state.update_game_time(delta_time)
        
        # Only update gameplay if in playing state
        if self.game_state.is_playing():
            # Update player with obstacle collision detection
            self.player.update(self.obstacle_manager)
            
            # Debug: Show player position and current color
            if hasattr(self, '_debug_counter'):
                self._debug_counter += 1
            else:
                self._debug_counter = 0
                
            # Print debug info every 60 frames (once per second at 60fps)
            if self._debug_counter % 60 == 0:
                print(f"[DEBUG] Player at ({self.player.center_x:.1f}, {self.player.center_y:.1f}), color: {self.player.current_color}")
                # Check nearby items
                nearby_items = self.item_manager.get_active_items_near(self.player.center_x, self.player.center_y, 100)
                print(f"[DEBUG] {len(nearby_items)} items within 100 units")
                if len(nearby_items) > 0:
                    closest = min(nearby_items, key=lambda item: ((item.center_x - self.player.center_x)**2 + (item.center_y - self.player.center_y)**2)**0.5)
                    distance = ((closest.center_x - self.player.center_x)**2 + (closest.center_y - self.player.center_y)**2)**0.5
                    print(f"[DEBUG] Closest item: {closest.type} ({closest.color_name}) at distance {distance:.1f}")
            
            # Check item collections with new color-based logic
            collected_value, collected_items = self.item_manager.check_collisions(self.player)
            if collected_items:
                for item in collected_items:
                    print(f"[GAME] Collected {item['type']} (color: {item['color_name']}) - Player color: {self.player.current_color}")
                    # Check if item color matches player color
                    if item["color_name"] == self.player.current_color:
                        # Correct color - add points
                        print(f"[GAME] Color match! Adding {item['value']} points")
                        self.game_state.add_score(item["value"])
                        # Update legacy score for compatibility
                        self.score = self.game_state.score
                        self.total_value += item["value"]
                    else:
                        # Wrong color - change player color and reset score
                        print(f"[GAME] Color mismatch! Changing player color from {self.player.current_color} to {item['color_name']} and resetting score")
                        self.player.change_color(item["color_name"])
                        self.game_state.reset_score()
                        # Update legacy score for compatibility
                        self.score = 0
                        self.total_value = 0
            
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
        margin_x = min(MARGIN_X, screen_width * 0.25)
        margin_y = min(MARGIN_Y, screen_height * 0.25)

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
        
        # Handle different input based on game state
        if self.game_state.is_playing():
            # Normal gameplay controls
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
                self.game_state.set_state(GameState.HIGH_SCORES)
        
        elif self.game_state.is_game_over():
            # Game over screen controls
            if key == arcade.key.ENTER:
                # Check if it's a high score
                if self.high_score_manager.is_high_score(self.game_state.final_score, self.game_state.final_time):
                    self.game_state.set_state(GameState.NAME_ENTRY)
                else:
                    self.game_state.set_state(GameState.HIGH_SCORES)
            elif key == arcade.key.R:
                self.setup()  # Start new game
            elif key == arcade.key.H:
                self.game_state.set_state(GameState.HIGH_SCORES)
        
        elif self.game_state.is_name_entry():
            # Name entry controls
            if key == arcade.key.ENTER:
                # Save the high score and show high scores
                position = self.high_score_manager.add_score(
                    self.game_state.entered_name or "Anonymous",
                    self.game_state.final_score,
                    self.game_state.final_time
                )
                self.game_state.score_position = position
                self.game_state.confirm_name()
            elif key == arcade.key.BACKSPACE:
                self.game_state.remove_name_character()
            else:
                # Handle character input
                if hasattr(arcade.key, 'A') and key >= arcade.key.A and key <= arcade.key.Z:
                    # Letter keys
                    char = chr(key).lower()
                    if modifiers & arcade.key.MOD_SHIFT:
                        char = char.upper()
                    self.game_state.add_name_character(char)
                elif key == arcade.key.SPACE:
                    self.game_state.add_name_character(" ")
                elif key >= arcade.key.KEY_0 and key <= arcade.key.KEY_9:
                    # Number keys
                    char = str(key - arcade.key.KEY_0)
                    self.game_state.add_name_character(char)
        
        elif self.game_state.is_high_scores():
            # High scores screen controls
            if key == arcade.key.R:
                self.setup()  # Start new game
            elif key == arcade.key.ESCAPE:
                self.game_state.set_state(GameState.PLAYING)
        
        logger.debug(f"=== KEY PRESS EVENT END ===")

    def on_key_release(self, key, modifiers):
        """Handle key release events"""
        # Only handle player movement releases during gameplay
        if self.game_state.is_playing():
            self.player.on_key_release(key, modifiers) 