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
from ursina import color, Vec2

# ----- Looking around -----
# Normally you look around with the MOUSE. On some setups (certain WSL
# installs) the window cannot "capture" the mouse, and then mouse-look feels
# stuck or frozen. So we also allow looking with the ARROW KEYS, and you can
# switch the mouse off completely if it misbehaves.
MOUSE_LOOK = True       # set False if your mouse can't turn the view properly
KEYBOARD_LOOK = True    # arrow keys turn the view as well (always handy)
LOOK_SPEED = 120        # arrow-key look speed (degrees per second)

# ----- Window -----
WINDOW_TITLE = "My First 3D FPS"
WINDOW_SIZE = (960, 540)          # (width, height) in pixels
FULLSCREEN = False
SHOW_FPS = True                   # show the frames-per-second counter

# ----- Player -----
PLAYER_SPEED = 5
# How fast the view turns when you move the mouse. SMALLER = calmer, easier
# to aim; BIGGER = whippy. (ursina's own default is 40, which is very fast.)
# The two numbers are (left-right, up-down) -- keep them equal unless you
# want looking up and down to feel different from turning.
MOUSE_SENSITIVITY = Vec2(10, 10)
PLAYER_MAX_HEALTH = 100           # how much damage you can take before dying

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

# ----- Ammo & reloading -----
# The gun has a MAGAZINE (the bullets loaded right now) and a RESERVE
# (the spare bullets in your pocket). Reloading moves bullets from the
# reserve into the magazine -- and takes time, so you are helpless while
# it happens. That waiting time is what makes reloading interesting!
MAG_SIZE = 12                 # how many bullets fit in one magazine
RESERVE_AMMO = 60             # spare bullets you start with
INFINITE_AMMO = False         # True = the reserve never runs out
RELOAD_TIME = 1.2             # seconds a reload takes
RELOAD_KEY = "r"              # press this to reload
AUTO_RELOAD = True            # click on an empty gun -> reload by itself
SHOOT_COOLDOWN = 0.15         # seconds between shots (stops machine-gun clicking)
# How the gun moves while reloading (purely for looks):
RELOAD_DIP = (0, -0.07, -0.05)  # (right, up, forward) offset -- it dips down
RELOAD_TILT = -25               # degrees it tilts while being reloaded

# ----- Sound -----
SOUND_ON = True               # set False to turn off all sound
SHOOT_SOUND = "shoot.wav"     # the sound file played when you shoot
SHOOT_VOLUME = 0.5            # 0.0 (silent) to 1.0 (full)
RELOAD_SOUND = "reload.wav"   # played when you start reloading
EMPTY_SOUND = "empty.wav"     # the "click" of an empty gun
HIT_SOUND = "hit.wav"         # the "ping" when a bullet hits an enemy
HIT_VOLUME = 0.4

# ----- Bullet -----
BULLET_SPEED = 40
BULLET_SCALE = 0.3
BULLET_LIFETIME = 3.0             # seconds before a bullet disappears
BULLET_COLOR = color.yellow
BULLET_DAMAGE = 1                 # how much health one bullet takes off an enemy
# How far in front of the camera a bullet appears. Keep it SMALL: a bullet
# only starts checking for hits from here, so a big number would make
# point-blank shots at an enemy standing right next to you miss.
BULLET_SPAWN_DISTANCE = 0.8

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

# ----- Enemies -----
# An enemy is a red block that walks towards you and hurts you if it gets
# close. It is NOT clever: a wall stops it, so the blocks in the map are
# your cover. Shoot it ENEMY_HEALTH times and it dies.
ENEMY_HEALTH = 3                  # bullets needed to kill one (with BULLET_DAMAGE = 1)
ENEMY_COLOR = color.red
# (width, height, depth). They are a bit TALLER than you (your eyes are 2
# units up), so the crosshair hits their chest without having to aim down.
ENEMY_SCALE = (1, 2.6, 1)
ENEMY_Y = 1.3                     # lifts the enemy so its feet touch the ground
                                  # (always half of the height above)
ENEMY_SPEED = 1.2                 # slower than PLAYER_SPEED (5), so you can run away
ENEMY_SIGHT_RANGE = 20            # starts chasing you when you are this close
ENEMY_ATTACK_RANGE = 2.0          # close enough to hit you
ENEMY_DAMAGE = 10                 # health you lose per hit
ENEMY_ATTACK_COOLDOWN = 1.0       # seconds between its hits
ENEMY_POINTS = 100                # score you get for killing one
ENEMY_HIT_FLASH = color.white     # colour it flashes when you shoot it
ENEMY_DEATH_TIME = 0.25           # seconds it takes to shrink away when it dies
SHOW_ENEMY_HEALTH_BARS = True     # the little green bar above each enemy
# Where the enemies start. Just like BLOCK_SPOTS -- add or remove (x, z)
# pairs to make the level harder or easier.
ENEMY_SPOTS = [
    (8, 9),
    (-8, 10),
    (0, -10),
    (13, 4),
    (-12, -4),
    (6, -8),
]

# ----- Crosshair -----
CROSSHAIR_COLOR = color.white

# ----- HUD (the numbers drawn on the screen) -----
SHOW_HUD = True
HUD_TEXT_COLOR = color.white
HUD_HURT_FLASH = color.rgba(255, 0, 0, 90)   # red screen flash when hurt
