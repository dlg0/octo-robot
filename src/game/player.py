import arcade

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

    def reset(self):
        self.x = START_X
        self.y = START_Y
        self.change_x = 0
        self.change_y = 0

    def update(self):
        self.x += self.change_x
        self.y += self.change_y
        # Keep player on screen
        self.x = max(PLAYER_RADIUS, min(self.x, 800 - PLAYER_RADIUS))
        self.y = max(PLAYER_RADIUS, min(self.y, 600 - PLAYER_RADIUS))

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