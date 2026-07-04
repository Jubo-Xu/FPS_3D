"""
entities.py  --  The "things" in our game, each written as its own CLASS.

WHY CLASSES?
A class lets us keep an object's LOOK and its BEHAVIOR together in one tidy
box. Each one is built on top of ursina's `Entity`, which is anything that
can appear in the 3D world.

A really nice ursina trick used below: if a class has an `update` method,
ursina calls it AUTOMATICALLY every frame -- so each bullet can move and
delete *itself*. No global list of bullets to manage!
"""
from ursina import Entity, camera, color, destroy, time, Audio
from ursina.prefabs.first_person_controller import FirstPersonController

import config


# ----------------------------------------------------------------------
# BULLET
# ----------------------------------------------------------------------
class Bullet(Entity):
    """A glowing ball that flies forward, then deletes itself."""

    def __init__(self, position, direction):
        # super().__init__ sets up the Entity (its look + where it starts).
        super().__init__(
            model="sphere",
            color=config.BULLET_COLOR,
            scale=config.BULLET_SCALE,
            position=position,
            collider="sphere",
        )
        self.direction = direction          # which way it flies
        self.life = config.BULLET_LIFETIME  # seconds left to live

    def update(self):
        """ursina calls this every frame, for THIS bullet on its own."""
        self.position += self.direction * config.BULLET_SPEED * time.dt
        self.life -= time.dt
        if self.life <= 0:
            destroy(self)                   # remove myself from the game


# ----------------------------------------------------------------------
# GUNS
# ----------------------------------------------------------------------
# We have a base "Gun" that knows how to SHOOT, and two kinds of gun that
# only differ in how they LOOK:
#   ModelGun -> uses the downloaded blaster.glb model
#   BoxGun   -> built by hand out of cubes
# Because they both inherit shoot() from Gun, the rest of the game can use
# either one without caring which it is. (This idea is called polymorphism.)
class Gun(Entity):
    """Base gun: handles shooting + sound. The LOOK is added by subclasses."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)        # set up the Entity (look, position...)
        # Load the shooting sound ONCE here, not on every shot (loading a file
        # is slow). autoplay=False means "don't play it yet -- wait until I
        # call .play()". We keep it in self.shoot_sound to reuse each shot.
        self.shoot_sound = None
        if config.SOUND_ON:
            try:
                self.shoot_sound = Audio(
                    config.SHOOT_SOUND,
                    volume=config.SHOOT_VOLUME,
                    autoplay=False,
                )
            except Exception:
                # No audio device (e.g. on WSL) -- just play silently.
                self.shoot_sound = None

    def shoot(self):
        """Play the sound and spawn a bullet flying where we are looking."""
        if self.shoot_sound:
            self.shoot_sound.play()
        Bullet(
            position=camera.world_position + camera.forward * 1.5,
            direction=camera.forward,
        )


class ModelGun(Gun):
    """A gun that uses the downloaded 3D model (blaster.glb)."""

    def __init__(self):
        super().__init__(
            parent=camera,                  # stick it to the camera
            model=config.GUN_MODEL,
            position=config.GUN_MODEL_POSITION,
            scale=config.GUN_MODEL_SCALE,
            rotation=config.GUN_MODEL_ROTATION,
        )


class BoxGun(Gun):
    """A gun we build ourselves from a few simple cubes."""

    def __init__(self):
        super().__init__(
            parent=camera,
            position=config.GUN_BOX_POSITION,
        )
        # The pieces are children of the gun, so they move together with it.
        # main body of the gun:
        Entity(parent=self, model="cube", color=color.gray,
               scale=(0.12, 0.12, 0.45), position=(0, 0, 0))
        # the barrel sticking out the front:
        Entity(parent=self, model="cube", color=color.dark_gray,
               scale=(0.05, 0.05, 0.35), position=(0, 0.02, 0.35))
        # the handle/grip pointing down:
        Entity(parent=self, model="cube", color=color.brown,
               scale=(0.08, 0.22, 0.1), position=(0, -0.15, -0.15))


def make_gun():
    """Build whichever gun config.GUN_TYPE asks for."""
    if config.GUN_TYPE == "boxes":
        return BoxGun()
    return ModelGun()


# ----------------------------------------------------------------------
# PLAYER
# ----------------------------------------------------------------------
class Player(FirstPersonController):
    """The player: walk + mouse-look + jump (from ursina), holding a gun."""

    def __init__(self):
        super().__init__(
            y=2, origin_y=-0.5,
            speed=config.PLAYER_SPEED,
            mouse_sensitivity=config.MOUSE_SENSITIVITY,
        )
        self.cursor.enabled = False   # hide ursina's default pink dot
        self.gun = make_gun()         # give the player a gun

        # The "base" zoom that the scroll wheel changes. Right-click aiming
        # zooms in on top of this, then snaps back to base_fov on release.
        self.base_fov = config.DEFAULT_FOV
        camera.fov = self.base_fov

    def input(self, key):
        """ursina calls this when a key/mouse button is pressed."""
        super().input(key)            # keep the built-in controls (jump, etc.)
        if key == "left mouse down":
            self.gun.shoot()

        # --- Scroll wheel: zoom in/out (changes the base view) ---
        if key == "scroll up":
            self.base_fov = max(config.ZOOM_MIN, self.base_fov - config.ZOOM_STEP)
            camera.fov = self.base_fov
        if key == "scroll down":
            self.base_fov = min(config.ZOOM_MAX, self.base_fov + config.ZOOM_STEP)
            camera.fov = self.base_fov

        # --- Hold right-click to aim (zoom in), release to go back ---
        if key == "right mouse down":
            camera.fov = config.AIM_FOV
        if key == "right mouse up":
            camera.fov = self.base_fov   # back to the scrolled zoom level


# ----------------------------------------------------------------------
# CROSSHAIR (the aiming "+" in the middle of the screen)
# ----------------------------------------------------------------------
class Crosshair(Entity):
    """Two thin white bars that together make a + in the screen center."""

    def __init__(self):
        super().__init__(parent=camera.ui)   # camera.ui = flat screen overlay
        Entity(parent=self, model="quad", color=config.CROSSHAIR_COLOR,
               scale=(0.03, 0.004))          # horizontal bar
        Entity(parent=self, model="quad", color=config.CROSSHAIR_COLOR,
               scale=(0.004, 0.03))          # vertical bar
