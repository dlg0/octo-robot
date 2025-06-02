import arcade
from arcade.camera import Camera2D
from .player import Player
from .item_manager import ItemManager
from .obstacle_manager import ObstacleManager
from .background_manager import BackgroundManager
from rendering.renderer import Renderer

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Octo-Robot - Enhanced World"
MARGIN_X = 200  # Margin from left/right edge
MARGIN_Y = 150  # Margin from top/bottom edge

class OctoRobotGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # Initialize game systems
        self.player = Player()
        self.item_manager = ItemManager()
        self.obstacle_manager = ObstacleManager()
        self.background_manager = BackgroundManager()
        
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

    def setup(self):
        """Initialize the game state"""
        self.player.reset()
        self.item_manager.reset()
        self.obstacle_manager.reset()
        self.background_manager.reset()
        self.score = 0
        self.total_value = 0
        self.camera.position = (0, 0)
        
        # Generate initial content around starting position
        self.update_world_generation()

    def on_draw(self):
        """Render the game"""
        self.clear()
        
        # Get camera position for rendering
        camera_x, camera_y = self.camera.position
        
        # Use camera for world rendering
        self.camera.use()
        
        # Draw in order: background -> obstacles -> items -> player
        self.renderer.draw_background(camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer.draw_obstacles(camera_x, camera_y)
        self.renderer.draw_items(camera_x, camera_y)
        self.renderer.draw_player()
        
        # Draw UI (it will handle its own positioning)
        self.renderer.draw_ui(self.score, self.total_value, camera_x, camera_y)

    def on_update(self, delta_time):
        """Update game logic"""
        # Update player with obstacle collision detection
        self.player.update(self.obstacle_manager)
        
        # Check item collections
        collected_value = self.item_manager.check_collisions(self.player)
        if collected_value > 0:
            self.score += 1  # Count of items collected
            self.total_value += collected_value  # Total value collected
        
        # Update camera to follow player
        self.scroll_camera_to_player()
        
        # Generate world content around player
        self.update_world_generation()

    def update_world_generation(self):
        """Update procedural generation around the player"""
        # Generate items around player position
        self.item_manager.update_generation(self.player.x, self.player.y)
        
        # Generate obstacles around player position
        self.obstacle_manager.update_generation(self.player.x, self.player.y)
        
        # Generate background around camera position
        camera_x, camera_y = self.camera.position
        self.background_manager.update_generation(camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT)

    def scroll_camera_to_player(self):
        """Smooth camera following with margins"""
        # Calculate the visible area based on camera's center position
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

        # Smooth camera movement for better experience
        current_x, current_y = self.camera.position
        lerp_factor = 0.1  # Adjust for smoother/snappier camera
        
        new_x = current_x + (target_x - current_x) * lerp_factor
        new_y = current_y + (target_y - current_y) * lerp_factor
        
        self.camera.position = (new_x, new_y)

    def on_key_press(self, key, modifiers):
        """Handle key press events"""
        self.player.on_key_press(key, modifiers)
        
        # Reset game with R key
        if key == arcade.key.R:
            self.setup()

    def on_key_release(self, key, modifiers):
        """Handle key release events"""
        self.player.on_key_release(key, modifiers) 