"""
main.py  --  The entry point. THIS is the file you run:

    python main.py

It just wires the pieces together:
  1. (WSL fix) force software rendering if there's no graphics card.
  2. Create the ursina app + window.
  3. Build the world, the player, the enemies, the crosshair and the HUD.
  4. Start the game loop.

The actual details live in the other files:
  config.py  -- all the tweakable numbers
  world.py     -- builds the level + places the enemies
  entities.py  -- the Player, Gun, Bullet, Enemy and HUD classes
"""
import os

# ----------------------------------------------------------------------
# WSL / no-GPU FIX  (must run BEFORE the 3D window is created)
# ----------------------------------------------------------------------
# On Windows-Subsystem-for-Linux there is usually no real graphics card for
# Linux (the folder /dev/dri is missing), which makes the 3D window open
# completely BLACK. Switching to "software rendering" (the CPU draws the 3D
# instead of a GPU) fixes it. On a normal computer this block does nothing.
if not os.path.exists("/dev/dri"):
    os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
    os.environ.setdefault("GALLIUM_DRIVER", "llvmpipe")

from ursina import Ursina, window, application

import config
from world import build_world, spawn_enemies
from entities import Player, Crosshair, HUD


def main():
    # Create the game application (this opens the window).
    app = Ursina()

    # Apply our window settings from config.py
    window.title = config.WINDOW_TITLE
    window.fullscreen = config.FULLSCREEN
    window.borderless = False
    window.size = config.WINDOW_SIZE
    window.fps_counter.enabled = config.SHOW_FPS
    window.exit_button.visible = False

    # Build everything. ORDER MATTERS a little here:
    #   the enemies need the player (to chase), and
    #   the HUD needs the player and the enemies (to count them).
    build_world()
    player = Player()              # creating it wires it into the game
    enemies = spawn_enemies(player)
    Crosshair()
    if config.SHOW_HUD:
        HUD(player, enemies)

    # Run the game until the window is closed.
    app.run()


# Quit with the ESC key. ursina automatically calls a top-level function
# named `input` whenever a key is pressed.
def input(key):
    if key == "escape":
        application.quit()


# Only run the game if THIS file was launched directly (not imported).
if __name__ == "__main__":
    main()
