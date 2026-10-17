"""
entities.py  --  The "things" in our game, each written as its own CLASS.

WHY CLASSES?
A class lets us keep an object's LOOK and its BEHAVIOR together in one tidy
box. Each one is built on top of ursina's `Entity`, which is anything that
can appear in the 3D world.

A really nice ursina trick used below: if a class has an `update` method,
ursina calls it AUTOMATICALLY every frame -- so each bullet can move and
delete *itself*. No global list of bullets to manage!

What lives in here:
  Enemy      -- a red block that chases you and can hurt you
  Bullet     -- flies forward and damages the enemy it hits
  Gun        -- shooting, AMMO and RELOADING (+ ModelGun / BoxGun looks)
  Player     -- you: walking, looking, shooting, health and score
  Crosshair  -- the + in the middle of the screen
  HUD        -- the ammo / health / score text drawn on top of the game
"""
from ursina import (Audio, Entity, Text, camera, clamp, color, destroy,
                    distance_xz, held_keys, lerp, mouse, raycast, time, Vec2,
                    Vec3, window)
from ursina.prefabs.first_person_controller import FirstPersonController

import config


# ----------------------------------------------------------------------
# HELPER: load a sound file safely
# ----------------------------------------------------------------------
# Loading a sound can fail (the file is missing, or the computer has no
# sound card -- WSL doesn't). We never want that to crash the game, so every
# sound goes through this one little function. It gives back either an Audio
# object or None, and the code that uses it always checks for None first.
#
# Reading a file is SLOW, so we must never do it while the game is running
# (imagine loading hit.wav again for every single bullet!). The _sounds
# dictionary remembers every sound we have already loaded, keyed by its
# filename, and hands back the same one next time it is asked for.
_sounds = {}

def load_sound(filename, volume):
    if not config.SOUND_ON:
        return None
    if filename not in _sounds:
        try:
            # autoplay=False means "don't play it yet -- wait until I call .play()"
            _sounds[filename] = Audio(filename, volume=volume, autoplay=False)
        except Exception:
            _sounds[filename] = None      # remember the failure too, so we
                                          # don't keep retrying every frame
    return _sounds[filename]


# ----------------------------------------------------------------------
# ENEMY
# ----------------------------------------------------------------------
class Enemy(Entity):
    """A red block that walks towards the player and hits them.

    It has HEALTH: every bullet takes some off, and at 0 it dies.
    It is deliberately not clever -- it walks straight at you and a wall
    stops it. That's what makes the blocks in the map useful as cover.
    """

    def __init__(self, position, target):
        super().__init__(
            model="cube",
            color=config.ENEMY_COLOR,
            scale=config.ENEMY_SCALE,
            position=position,
            collider="box",
        )
        self.target = target              # who it chases: the Player
        self.health = config.ENEMY_HEALTH
        self.dead = False
        self.attack_timer = 0.0           # seconds until it can hit again

        # A little green bar floating above its head, in two parts:
        #   bar_pivot  -- an invisible point above the head. billboard=True
        #                 means "always turn to face the camera", so the bar
        #                 is readable from any angle. Its scale undoes the
        #                 enemy's stretched scale, so the bar isn't squashed.
        #   health_bar -- the green quad itself. origin_x=-0.5 pins it to its
        #                 own LEFT edge, so making it narrower empties it
        #                 from the right, like a real health bar.
        self.bar_pivot = Entity(
            parent=self,                  # child -> it moves with the enemy
            position=(0, 0.6, 0),         # just above the head
            scale=(1 / config.ENEMY_SCALE[0], 1 / config.ENEMY_SCALE[1], 1),
            billboard=True,
            enabled=config.SHOW_ENEMY_HEALTH_BARS,
        )
        self.health_bar = Entity(
            parent=self.bar_pivot,
            model="quad",
            color=color.lime,
            origin_x=-0.5,
            position=(-0.5, 0, 0),
            scale=(1, 0.12),
        )

    # ----- being shot -------------------------------------------------
    def take_damage(self, amount):
        """Called by a Bullet that hits us."""
        if self.dead:
            return
        self.health -= amount
        self.blink(config.ENEMY_HIT_FLASH)      # quick flash so the hit is visible

        # Shrink the health bar to match the health that is left, and fade
        # its colour from green towards red. `lerp` means "mix these two
        # colours", with 1.0 = all green and 0.0 = all red.
        left = max(0, self.health) / config.ENEMY_HEALTH
        self.health_bar.scale_x = left
        self.health_bar.color = lerp(color.red, color.lime, left)

        if self.health <= 0:
            self.die()

    def die(self):
        self.dead = True
        self.collider = None              # bullets fly through a dying enemy
        self.bar_pivot.enabled = False    # hide the health bar
        self.target.add_score(config.ENEMY_POINTS)
        # Shrink to nothing, THEN delete. `delay` waits before destroying.
        self.animate_scale(0, duration=config.ENEMY_DEATH_TIME)
        destroy(self, delay=config.ENEMY_DEATH_TIME)

    # ----- thinking, once per frame -----------------------------------
    def update(self):
        if self.dead or not self.target.alive:
            return

        # distance_xz ignores the height difference, so a player standing on
        # a block still counts as "close".
        gap = distance_xz(self, self.target)
        if gap > config.ENEMY_SIGHT_RANGE:
            return                        # too far away: hasn't noticed you

        self.look_at_2d(self.target, "y")  # turn to face the player

        if gap > config.ENEMY_ATTACK_RANGE:
            self.walk_towards_target()
        else:
            # Close enough to attack, but only once every cooldown.
            self.attack_timer -= time.dt
            if self.attack_timer <= 0:
                self.attack_timer = config.ENEMY_ATTACK_COOLDOWN
                self.target.take_damage(config.ENEMY_DAMAGE)

    def walk_towards_target(self):
        """Take one step towards the player -- unless something is in the way."""
        # The direction from me to the player, flattened so we don't fly up.
        towards = self.target.world_position - self.world_position
        towards.y = 0
        towards = towards.normalized()

        # Look a short distance ahead with a "raycast" (an invisible laser
        # beam). If it hits something, there's a wall there, so don't move.
        ahead = raycast(self.world_position, towards, distance=1, ignore=(self,))
        if not ahead.hit:
            self.position += towards * config.ENEMY_SPEED * time.dt


# ----------------------------------------------------------------------
# BULLET
# ----------------------------------------------------------------------
class Bullet(Entity):
    """A glowing ball that flies forward, hits things, then deletes itself."""

    def __init__(self, position, direction):
        # super().__init__ sets up the Entity (its look + where it starts).
        # NOTE: no collider here on purpose -- see update() below.
        super().__init__(
            model="sphere",
            color=config.BULLET_COLOR,
            scale=config.BULLET_SCALE,
            position=position,
        )
        self.direction = direction          # which way it flies
        self.life = config.BULLET_LIFETIME  # seconds left to live
        self.hit_sound = load_sound(config.HIT_SOUND, config.HIT_VOLUME)

    def update(self):
        """ursina calls this every frame, for THIS bullet on its own."""
        step = config.BULLET_SPEED * time.dt     # how far we fly this frame

        # HOW DO WE KNOW WE HIT SOMETHING?
        # A bullet is fast: at 40 units/second it jumps most of a metre
        # between two frames, so just asking "am I inside an enemy now?"
        # would sometimes miss (the bullet would appear on the far side).
        # Instead we check the PATH it is about to fly with a `raycast` --
        # an invisible laser beam from here, in the direction we're going,
        # exactly as long as this frame's step.
        hit = raycast(self.world_position, self.direction, distance=step,
                      ignore=(self,))
        if hit.hit:
            # isinstance(x, Enemy) asks "is this thing an Enemy?" -- walls
            # and the ground are just plain Entities, so they only stop the
            # bullet, they don't take damage.
            if isinstance(hit.entity, Enemy):
                hit.entity.take_damage(config.BULLET_DAMAGE)
                if self.hit_sound:
                    self.hit_sound.play()
            destroy(self)                   # the bullet is used up either way
            return

        self.position += self.direction * step
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
    """Base gun: shooting, ammo + reloading. The LOOK is added by subclasses.

    THE AMMO IDEA
    -------------
      self.ammo    = bullets in the magazine (what you can fire right now)
      self.reserve = spare bullets in your pocket
    Shooting takes 1 off `ammo`. Reloading waits RELOAD_TIME seconds and then
    moves bullets from `reserve` into `ammo`. While the timer is running you
    cannot shoot -- that pause is the whole point of a reload.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)        # set up the Entity (look, position...)
        # Remember where the gun normally sits, so the reload animation can
        # move it away and then come back to exactly this spot.
        self.base_position = self.position
        self.base_rotation = self.rotation

        # Load the sounds ONCE here, not on every shot (loading a file is slow).
        self.shoot_sound = load_sound(config.SHOOT_SOUND, config.SHOOT_VOLUME)
        self.reload_sound = load_sound(config.RELOAD_SOUND, config.SHOOT_VOLUME)
        self.empty_sound = load_sound(config.EMPTY_SOUND, config.SHOOT_VOLUME)

        # --- the ammo state ---
        self.ammo = config.MAG_SIZE          # magazine starts full
        self.reserve = config.RESERVE_AMMO   # spare bullets
        self.reload_timer = 0.0              # seconds of reloading left (0 = not reloading)
        self.shoot_timer = 0.0               # seconds until we may shoot again

    # A "property" is a method you read like a plain variable:
    #   gun.is_reloading     (no brackets!)
    @property
    def is_reloading(self):
        return self.reload_timer > 0

    def update(self):
        """Count both timers down. ursina calls this every frame."""
        if self.reload_timer > 0:
            self.reload_timer -= time.dt
            if self.reload_timer <= 0:
                self.finish_reload()     # the wait is over: fill the magazine
        if self.shoot_timer > 0:
            self.shoot_timer -= time.dt

    # ----- shooting ---------------------------------------------------
    def shoot(self):
        """Fire one bullet -- if we are allowed to."""
        if self.is_reloading:
            return                        # busy reloading: nothing happens
        if self.shoot_timer > 0:
            return                        # fired too recently

        if self.ammo <= 0:
            # Empty! Just a sad little click.
            if self.empty_sound:
                self.empty_sound.play()
            if config.AUTO_RELOAD:
                self.reload()
            return

        self.ammo -= 1                    # one bullet leaves the magazine
        self.shoot_timer = config.SHOOT_COOLDOWN
        if self.shoot_sound:
            self.shoot_sound.play()
        Bullet(
            position=camera.world_position
            + camera.forward * config.BULLET_SPAWN_DISTANCE,
            direction=camera.forward,
        )

    # ----- reloading --------------------------------------------------
    def reload(self):
        """START a reload (the magazine is only filled when the timer ends)."""
        if self.is_reloading:
            return                        # already reloading
        if self.ammo >= config.MAG_SIZE:
            return                        # magazine is already full
        if self.reserve <= 0 and not config.INFINITE_AMMO:
            return                        # no spare bullets left at all

        self.reload_timer = config.RELOAD_TIME
        if self.reload_sound:
            self.reload_sound.play()

        # Just for looks: dip and tilt the gun out of the way.
        self.animate_position(self.base_position + Vec3(*config.RELOAD_DIP),
                              duration=0.15)
        self.animate_rotation(self.base_rotation + Vec3(config.RELOAD_TILT, 0, 0),
                              duration=0.15)

    def finish_reload(self):
        """The timer ran out: move bullets from the reserve into the magazine."""
        self.reload_timer = 0
        needed = config.MAG_SIZE - self.ammo
        if config.INFINITE_AMMO:
            taken = needed                       # pocket never runs out
        else:
            taken = min(needed, self.reserve)    # or however many we still have
            self.reserve -= taken
        self.ammo += taken

        # Bring the gun back to its normal place.
        self.animate_position(self.base_position, duration=0.15)
        self.animate_rotation(self.base_rotation, duration=0.15)


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
    """The player: walk + mouse-look + jump (from ursina), holding a gun.

    The player also keeps the things the HUD wants to show: health, score
    and whether we are still alive.
    """

    def __init__(self):
        super().__init__(
            y=2, origin_y=-0.5,
            speed=config.PLAYER_SPEED,
            mouse_sensitivity=config.MOUSE_SENSITIVITY,
        )
        self.cursor.enabled = False   # hide ursina's default pink dot
        self.gun = make_gun()         # give the player a gun

        # Mouse-look is on by default. If the window can't "capture" the
        # mouse (this happens on some WSL setups) looking around feels stuck,
        # so config.MOUSE_LOOK = False switches the mouse off and frees the
        # cursor -- you then look around with the arrow keys, which work
        # either way (see look_with_keys below).
        if not config.MOUSE_LOOK:
            self.mouse_sensitivity = Vec2(0, 0)
            mouse.locked = False
            mouse.visible = True

        # The "base" zoom that the scroll wheel changes. Right-click aiming
        # zooms in on top of this, then snaps back to base_fov on release.
        self.base_fov = config.DEFAULT_FOV
        camera.fov = self.base_fov

        # --- how we are doing ---
        self.max_health = config.PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.alive = True
        self.score = 0
        self.kills = 0

    # ----- getting hurt ----------------------------------------------
    def take_damage(self, amount):
        """Called by an Enemy standing next to us."""
        if not self.alive:
            return
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        self.alive = False
        mouse.locked = False      # give the mouse cursor back
        # NOTE: we do NOT disable the player entity -- the camera is attached
        # to it, so turning it off would black out the screen. The `alive`
        # flag, checked in update() and input(), is what actually stops us
        # moving and shooting.

    def add_score(self, points):
        """Called by an Enemy when we kill it."""
        self.score += points
        self.kills += 1

    def update(self):
        if not self.alive:
            return                # dead players don't walk or look around
        super().update()          # ursina's walking / looking / gravity
        if config.KEYBOARD_LOOK:
            self.look_with_keys()

    def look_with_keys(self):
        """Arrow-key looking, on top of (or instead of) the mouse.

        held_keys['left arrow'] is 1 while the key is held down and 0 when
        it isn't, so (right - left) is +1, 0 or -1: the direction to turn.
        """
        turn = held_keys["right arrow"] - held_keys["left arrow"]
        pitch = held_keys["down arrow"] - held_keys["up arrow"]
        self.rotation_y += turn * config.LOOK_SPEED * time.dt
        # camera_pivot is the "neck": tilting it looks up and down. clamp()
        # keeps it between -90 and +90 so we can't look upside down.
        self.camera_pivot.rotation_x = clamp(
            self.camera_pivot.rotation_x + pitch * config.LOOK_SPEED * time.dt,
            -90, 90)

    def input(self, key):
        """ursina calls this when a key/mouse button is pressed."""
        if not self.alive:
            return
        super().input(key)            # keep the built-in controls (jump, etc.)
        if key == "left mouse down":
            self.gun.shoot()

        # --- Reload ---
        if key == config.RELOAD_KEY:
            self.gun.reload()

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


# ----------------------------------------------------------------------
# HUD (Heads-Up Display: the info drawn on top of the game)
# ----------------------------------------------------------------------
# Everything here is parented to camera.ui, the flat 2D overlay. In ui
# coordinates the screen centre is (0, 0), the top is y = 0.5 and the bottom
# is y = -0.5. The sides are +/- 0.5 * window.aspect_ratio (wider than tall).
#
# The HUD does not DECIDE anything -- it only LOOKS at the player and the
# enemies every frame and writes down what it sees. Keeping "the rules" and
# "the display" apart like this is a really useful habit.
class HUD(Entity):
    """Shows ammo, health, score, and the game over / you win message."""

    def __init__(self, player, enemies):
        super().__init__(parent=camera.ui)
        self.player = player
        self.enemies = enemies
        self.last_health = player.health      # to notice when we get hurt
        self.shown = {}                       # what each text says right now

        edge = 0.5 * window.aspect_ratio      # x of the right screen edge

        # background=True puts a dark panel behind the letters. Without it,
        # white text disappears against the white gun or a bright sky.
        # --- ammo, bottom right: "12 / 60" ---
        self.ammo_text = Text(
            parent=self, text="0 / 0", color=config.HUD_TEXT_COLOR,
            origin=(0.5, -0.5), position=(edge - 0.05, -0.45), scale=1.6,
            background=True,
        )
        # --- "RELOADING..." just above the ammo ---
        self.reload_text = Text(
            parent=self, text="RELOADING...", color=color.yellow,
            origin=(0.5, -0.5), position=(edge - 0.05, -0.36), scale=1.1,
            background=True, enabled=False,
        )
        # --- score, top left ---
        self.score_text = Text(
            parent=self, text="Score 0", color=config.HUD_TEXT_COLOR,
            origin=(-0.5, 0.5), position=(-edge + 0.05, 0.47), scale=1.1,
            background=True,
        )

        # --- health bar, bottom left (two quads: dark track + red fill) ---
        self.health_track = Entity(
            parent=self, model="quad", color=color.black66,
            origin=(-0.5, -0.5), position=(-edge + 0.05, -0.45),
            scale=(0.3, 0.03),
        )
        # The fill is a CHILD of the track, so it sits exactly on top of it.
        # origin=(-0.5, -0.5) pins it to its own bottom-left corner, which
        # means shrinking scale_x empties the bar from the right.
        self.health_fill = Entity(
            parent=self.health_track, model="quad", color=color.red,
            origin=(-0.5, -0.5), position=(0, 0, -0.01),
            scale=(1, 1),
        )
        self.health_text = Text(
            parent=self, text="HP 0", color=config.HUD_TEXT_COLOR,
            origin=(-0.5, -0.5), position=(-edge + 0.05, -0.40), scale=1.1,
            background=True,
        )

        # --- a red flash over the whole screen when we get hit ---
        self.hurt_flash = Entity(
            parent=self, model="quad", color=config.HUD_HURT_FLASH,
            scale=(window.aspect_ratio * 1.1, 1.1), z=0.1, enabled=False,
        )

        # --- the big message in the middle (hidden until the game ends) ---
        self.message = Text(
            parent=self, text="...", color=color.white, origin=(0, 0),
            position=(0, 0.1), scale=3, background=True, enabled=False,
        )

    def enemies_left(self):
        """Count the enemies that are still alive."""
        return len([e for e in self.enemies if not e.dead])

    def set_text(self, name, new_text):
        """Change one of our Texts -- but only if it really changed.

        The dark background panel does not resize by itself, so we rebuild
        it here. Doing that 60 times a second would be wasteful, which is
        exactly why we check first whether anything is different.
        """
        if self.shown.get(name) == new_text:
            return
        self.shown[name] = new_text
        text_entity = getattr(self, name)
        text_entity.text = new_text
        text_entity.background = True     # rebuild the panel at the new size

    def update(self):
        gun = self.player.gun

        # --- ammo ---
        if config.INFINITE_AMMO:
            self.set_text("ammo_text", "{} / oo".format(gun.ammo))
        else:
            self.set_text("ammo_text", "{} / {}".format(gun.ammo, gun.reserve))
        # Red numbers when the magazine is empty, so it's obvious why
        # clicking does nothing.
        self.ammo_text.color = color.red if gun.ammo == 0 else config.HUD_TEXT_COLOR
        self.reload_text.enabled = gun.is_reloading

        # --- health ---
        fraction = self.player.health / self.player.max_health
        self.health_fill.scale_x = max(0.0001, fraction)   # 0 would hide it oddly
        self.health_fill.color = lerp(color.red, color.lime, fraction)
        self.set_text("health_text", "HP {}".format(int(self.player.health)))

        # Did the health drop since last frame? Then flash the screen red.
        if self.player.health < self.last_health:
            self.hurt_flash.enabled = True
            self.hurt_flash.color = config.HUD_HURT_FLASH
            self.hurt_flash.animate_color(color.clear, duration=0.4)
        self.last_health = self.player.health

        # --- score ---
        self.set_text("score_text", "Score {}    Enemies left: {}".format(
            self.player.score, self.enemies_left()))

        # --- the end of the game ---
        if not self.player.alive:
            self.show_message("GAME OVER\nPress ESC to quit", color.red)
        elif self.enemies_left() == 0:
            self.show_message("YOU WIN!\nScore: {}".format(self.player.score),
                              color.lime)

    def show_message(self, text, text_color):
        self.set_text("message", text)
        self.message.color = text_color
        self.message.enabled = True
