#!/usr/bin/env python3
"""
Main entry point for the Octo-Robot game.
"""

import arcade
from game.octo_robot_game import OctoRobotGame

def main():
    """Run the Octo-Robot game"""
    print("Starting Octo-Robot Enhanced World!")
    print("\nControls:")
    print("- WASD or Arrow Keys: Move the robot")
    print("- F: Toggle fullscreen mode")
    print("- R: Reset the game")
    print("- ESC: Exit the game")
    print("\nCollect items to increase your score!")
    print("Navigate around obstacles in this infinite world.\n")
    
    # Create and start the game
    game = OctoRobotGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main() 