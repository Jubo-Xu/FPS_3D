"""
config.py  --  ALL the tweakable numbers for the game, in one place.

This file holds no game logic -- just values. When you (or your student)
want to experiment ("make the gun bigger", "walk faster", "more blocks"),
you change a number HERE and never have to dig through the real code.

The other files read these values, e.g.  config.PLAYER_SPEED

NOTE: this file is deliberately NOT called "settings.py" -- ursina treats a
file named settings.py as its own engine-config file and auto-runs it, which
is not what we want. So we call ours "config.py" instead.
"""
import sys
import platform

from ursina import color, Vec2

# ----- Input fallback for WSL -----
# WSL can't "capture" the mouse, so FPS mouse-look doesn't work there (the
# cursor gets stuck and it feels frozen). When we detect WSL, we look around
# with the ARROW KEYS instead and keep the mouse cursor free. On Windows or
# normal Linux, regular mouse-look is used.
def _running_in_wsl():
    return sys.platform == "linux" and "microsoft" in platform.uname().release.lower()

KEYBOARD_LOOK = _running_in_wsl()   # set to True/False yourself to force it
LOOK_SPEED = 120                    # arrow-key look speed (degrees per second)

# ----- Window -----
WINDOW_TITLE = "My First 3D FPS"
WINDOW_SIZE = (960, 540)          # (width, height) in pixels
FULLSCREEN = False
SHOW_FPS = True                   # show the frames-per-second counter

# ----- Player -----
PLAYER_SPEED = 5
MOUSE_SENSITIVITY = Vec2(20, 20)  # smaller = calmer looking around (default 40)

# ----- View / zoom -----
# "FOV" = field of view: how wide an angle the camera sees.
#   smaller FOV = zoomed IN (narrow view)   |   larger FOV = zoomed OUT (wide)
DEFAULT_FOV = 90      # normal field of view
AIM_FOV = 40          # zoomed-in view while you HOLD right-click (aim down sights)
ZOOM_STEP = 5         # how much one scroll-wheel notch changes the zoom
ZOOM_MIN = 30         # most you can zoom IN  with the scroll wheel
ZOOM_MAX = 100        # most you can zoom OUT with the scroll wheel

# ----- Gun -----
# We support TWO kinds of gun, and you can switch between them by changing
# this one word:
#   "model" -> use the downloaded 3D model file (blaster.glb)
#   "boxes" -> use a gun we build ourselves out of simple cubes
GUN_TYPE = "model"

# ...settings for the "model" gun (blaster.glb):
GUN_MODEL = "blaster.glb"             # the 3D model file in this folder
GUN_MODEL_POSITION = (0.3, -0.25, 0.5)  # (right, up, forward) from the camera
GUN_MODEL_SCALE = 0.7
GUN_MODEL_ROTATION = (0, 180, 0)      # if the barrel points wrong, try (0,0,0)

# ...settings for the "boxes" gun (built by hand):
GUN_BOX_POSITION = (0.35, -0.28, 0.6)

# ----- Sound -----
SOUND_ON = True               # set False to turn off all sound
SHOOT_SOUND = "shoot.wav"     # the sound file played when you shoot
SHOOT_VOLUME = 0.5            # 0.0 (silent) to 1.0 (full)

# ----- Bullet -----
BULLET_SPEED = 40
BULLET_SCALE = 0.3
BULLET_LIFETIME = 3.0             # seconds before a bullet disappears
BULLET_COLOR = color.yellow

# ----- World / level -----
GROUND_SIZE = 50
GROUND_COLOR = color.green.tint(-0.3)
BLOCK_TEXTURE = "brick"
BLOCK_COLOR = color.azure
BLOCK_SCALE = (2, 3, 2)
# Each (x, z) is where a block/pillar will stand. Add or remove spots to
# redesign the map -- this is the most fun thing for a student to edit!
BLOCK_SPOTS = [
    (5, 5), (5, 8), (5, 11),
    (-6, 3), (-6, 6), (-9, 6),
    (0, 12), (3, 12), (-3, 12),
    (10, -4), (10, -1),
]

# ----- Crosshair -----
CROSSHAIR_COLOR = color.white
