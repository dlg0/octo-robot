import arcade
import math

PLAYER_SPEED = 5
PLAYER_RADIUS = 25
START_X = 100
START_Y = 100

class Player:
    def __init__(self):
        self.x = START_X
        self.y = START_Y
        self.change_x = 0
        self.change_y = 0
        self.previous_x = START_X
        self.previous_y = START_Y

    def reset(self):
        self.x = START_X
        self.y = START_Y
        self.change_x = 0
        self.change_y = 0
        self.previous_x = START_X
        self.previous_y = START_Y

    def update(self, obstacle_manager=None):
        # Store previous position for collision resolution
        self.previous_x = self.x
        self.previous_y = self.y
        
        # Calculate new position
        new_x = self.x + self.change_x
        new_y = self.y + self.change_y
        
        # Check for obstacle collisions if obstacle manager is provided
        if obstacle_manager:
            # Check X movement first
            if self.change_x != 0:
                collision = obstacle_manager.check_collision(new_x, self.y, PLAYER_RADIUS)
                if collision:
                    # Collision on X axis, don't move horizontally
                    new_x = self.x
            
            # Check Y movement
            if self.change_y != 0:
                collision = obstacle_manager.check_collision(new_x, new_y, PLAYER_RADIUS)
                if collision:
                    # Collision on Y axis, don't move vertically
                    new_y = self.y
        
        # Update position
        self.x = new_x
        self.y = new_y

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
            'left': self.x - PLAYER_RADIUS,
            'right': self.x + PLAYER_RADIUS,
            'bottom': self.y - PLAYER_RADIUS,
            'top': self.y + PLAYER_RADIUS
        } 