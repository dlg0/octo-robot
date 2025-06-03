import arcade
import math
from PIL import Image, ImageDraw # For texture generation

PLAYER_SPEED = 10 
PLAYER_RADIUS = 25
START_X = 100
START_Y = 100

# Define available player colors that match item colors exactly
PLAYER_COLORS = {
    "purple": arcade.color.PURPLE,  # Match the crystal color exactly
    "yellow": arcade.color.YELLOW,  # Match the battery color exactly
    "gray": arcade.color.GRAY,      # Match the gear color exactly
    "cyan": arcade.color.CYAN,      # Match the gem color exactly
    "red": arcade.color.RED         # Match the power core color exactly
}

_texture_cache: dict[str, arcade.Texture] = {}

def _get_player_texture(color_tuple: tuple) -> arcade.Texture:
    color_key = f"player_{color_tuple[0]}_{color_tuple[1]}_{color_tuple[2]}"
    if color_key in _texture_cache:
        return _texture_cache[color_key]

    diameter = PLAYER_RADIUS * 2
    img = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
    draw_img = ImageDraw.Draw(img)
    
    # Ensure we have a proper color tuple (handle both RGB and RGBA)
    if len(color_tuple) == 3:
        fill_color = color_tuple + (255,)  # Add alpha
    else:
        fill_color = color_tuple
    
    # Draw the main circle with the player's color
    draw_img.ellipse((0, 0, diameter - 1, diameter - 1), fill=fill_color)
    
    # Add a darker border for better visibility
    border_color = tuple(max(0, c - 50) for c in fill_color[:3]) + (255,)
    draw_img.ellipse((0, 0, diameter - 1, diameter - 1), outline=border_color, width=2)
    
    # Add some inner detail to make color changes more obvious
    inner_radius = int(PLAYER_RADIUS * 0.6)
    inner_left = (diameter - inner_radius * 2) // 2
    inner_top = (diameter - inner_radius * 2) // 2
    inner_right = inner_left + inner_radius * 2
    inner_bottom = inner_top + inner_radius * 2
    
    # Lighter inner circle for depth
    lighter_color = tuple(min(255, c + 30) for c in fill_color[:3]) + (255,)
    draw_img.ellipse((inner_left, inner_top, inner_right, inner_bottom), fill=lighter_color)
    
    texture = arcade.Texture(image=img, name=f"player_texture_{color_key}")
    _texture_cache[color_key] = texture
    return texture

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.current_color = "yellow"  # Start with yellow instead of purple to make changes more visible
        self.color_tuple = PLAYER_COLORS[self.current_color]
        self.texture = _get_player_texture(self.color_tuple)
        print(f"[PLAYER INIT] Starting with color: {self.current_color}, tuple: {self.color_tuple}")
        print(f"[PLAYER INIT] Texture created: {self.texture}")
        self.center_x = START_X
        self.center_y = START_Y
        # self.change_x and self.change_y are already part of arcade.Sprite
        self.previous_center_x = START_X # For collision rollback logic
        self.previous_center_y = START_Y # For collision rollback logic

    def change_color(self, new_color: str):
        """Change the player's color and update the texture"""
        if new_color in PLAYER_COLORS:
            old_color = self.current_color
            self.current_color = new_color
            self.color_tuple = PLAYER_COLORS[new_color]
            
            # Force regeneration of texture (clear cache for this color)
            color_key = f"player_{self.color_tuple[0]}_{self.color_tuple[1]}_{self.color_tuple[2]}"
            if color_key in _texture_cache:
                del _texture_cache[color_key]
                print(f"[PLAYER] Cleared cached texture for {color_key}")
            
            self.texture = _get_player_texture(self.color_tuple)
            print(f"[PLAYER] Color changed from {old_color} to {new_color}")
            print(f"[PLAYER] New color tuple: {self.color_tuple}")
            print(f"[PLAYER] New texture: {self.texture}")
        else:
            print(f"[PLAYER] Warning: Unknown color '{new_color}', available colors: {list(PLAYER_COLORS.keys())}")

    def reset(self):
        self.center_x = START_X
        self.center_y = START_Y
        self.change_x = 0
        self.change_y = 0
        self.previous_center_x = START_X
        self.previous_center_y = START_Y
        # Reset to default color (yellow for better visibility)
        self.change_color("yellow")

    def update(self, obstacle_manager=None):
        # Store previous position for collision resolution
        self.previous_center_x = self.center_x
        self.previous_center_y = self.center_y
        
        # Calculate potential new position based on current change_x, change_y
        # arcade.Sprite.update() would do this, but we need to interleave collision checks.
        potential_center_x = self.center_x + self.change_x
        potential_center_y = self.center_y + self.change_y
        
        # Target positions after collision checks
        target_x = potential_center_x
        target_y = potential_center_y

        if obstacle_manager:
            # Check X movement first
            if self.change_x != 0:
                # Temporarily move to check X collision
                original_x = self.center_x
                self.center_x = potential_center_x
                # Pass the player sprite (self) to the obstacle manager's collision check
                collision_info = obstacle_manager.check_collision(self) 
                self.center_x = original_x # Revert to original position before final assignment
                if collision_info:
                    target_x = self.previous_center_x # Don't move horizontally
            
            # Check Y movement (potentially from new X or old X if X-collision)
            if self.change_y != 0:
                original_y = self.center_y
                # For Y check, use the target_x that has already been resolved for X collisions
                # And temporarily apply potential_center_y for the check
                current_x_for_y_check = target_x 
                original_x_for_y_check = self.center_x # Store current center_x before changing it for check
                
                self.center_x = current_x_for_y_check
                self.center_y = potential_center_y
                collision_info = obstacle_manager.check_collision(self)
                self.center_x = original_x_for_y_check # Restore center_x
                self.center_y = original_y # Restore center_y
                if collision_info:
                    target_y = self.previous_center_y # Don't move vertically
        
        # Update actual position
        self.center_x = target_x
        self.center_y = target_y
        
        # Call super().update() if you want sprite animations or other built-in updates
        # super().update() # This would also add change_x/y to center_x/y if not handled above

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.change_x = PLAYER_SPEED
        elif key == arcade.key.UP or key == arcade.key.W:
            self.change_y = PLAYER_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.change_y = -PLAYER_SPEED

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            if self.change_x < 0:
                self.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            if self.change_x > 0:
                self.change_x = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            if self.change_y > 0:
                self.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            if self.change_y < 0:
                self.change_y = 0

    def get_bounds(self):
        """Get player bounding box for collision detection"""
        return {
            'left': self.center_x - PLAYER_RADIUS,
            'right': self.center_x + PLAYER_RADIUS,
            'bottom': self.center_y - PLAYER_RADIUS,
            'top': self.center_y + PLAYER_RADIUS
        } 