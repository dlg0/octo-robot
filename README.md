# Octo-Robot

A 2D adventure game where you control a robotic octopus exploring a world, collecting items, and upgrading abilities to progress through different levels. Built with Python and the Arcade library.

## Features
- Control Octo-Robot (move left/right, up/down)
- Explore a simple world
- Collect items (batteries, gears)
- See your collection count
- Clean code structure for easy learning and extension

## Requirements
- Python 3.10 or higher
- [Arcade](https://api.arcade.academy/) 3.2.0
- [uv](https://github.com/astral-sh/uv) (for all Python package management)

## Installation
1. **Install [uv](https://github.com/astral-sh/uv) if you haven't already:**
   ```sh
   curl -Ls https://astral.sh/uv/install.sh | sh
   # or see uv docs for your platform
   ```
2. **Install dependencies using uv:**
   ```sh
   uv pip install -r requirements.txt
   ```

## Running the Game
Start the game using the only supported method:
```sh
uv run octo-robot
```

## Project Structure
```
octo-robot/
  assets/           # Game art, sounds, etc.
  src/              # Game source code
    main.py         # Entry point
    game/           # Game logic (movement, collection, etc.)
    rendering/      # Rendering code (drawing, UI)
```

## Learning & Contributing
This project is designed for learning and fun! Contributions and suggestions are welcome, especially from kids and families.

---
Enjoy exploring with Octo-Robot!
