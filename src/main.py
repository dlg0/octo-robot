#!/usr/bin/env python3
"""
Main entry point for the Octo-Robot game.
"""

import arcade
from game.octo_robot_game import OctoRobotGame

def main():
    """Run the Octo-Robot game"""
    print("Starting Octo-Robot Enhanced World!")
    print("\n=== GAME OBJECTIVE ===")
    print("Collect 100 points as fast as possible!")
    print("• Collect dots that match your current color to gain points")
    print("• If you collect a dot of a different color:")
    print("  - Your color changes to that dot's color")
    print("  - Your score resets to 0")
    print("\n=== CONTROLS ===")
    print("- WASD or Arrow Keys: Move the robot")
    print("- F: Toggle fullscreen mode")
    print("- R: Reset the game")
    print("- H: View high scores")
    print("- ESC: Exit the game")
    print("\n=== SCORING ===")
    print("• Yellow dots (batteries): 1 point")
    print("• Gray dots (gears): 2 points")
    print("• Cyan dots (gems): 5 points")
    print("• Purple dots (crystals): 10 points")
    print("• Red dots (power cores): 20 points")
    print("\nYour best times to reach 100 points will be saved!")
    print("Navigate around obstacles in this infinite world.\n")
    
    # Create and start the game
    game = OctoRobotGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main() 