# 3D FPS starters (for teaching)

Two ways to make a first-person shooter in Python, from the same folder.

| What | Files | Best for |
|------|-----------|----------|
| **Real 3D FPS** (ursina engine) | `main.py` + `config.py` + `entities.py` + `world.py` | The "wow, I made a real game!" hook. Run `main.py`. |
| **Raycaster** (pure pygame) | `raycaster.py` | Teaching how 3D *actually* works. No engine — we fake 3D with math. |

### The ursina project files
- **`main.py`** — the file you run. Wires everything together and starts the game.
- **`config.py`** — every tweakable number (speed, gun, ammo, enemies, map...) in one place.
- **`entities.py`** — the `Enemy`, `Bullet`, `Gun`, `Player`, `Crosshair`, `HUD` classes.
- **`world.py`** — builds the level (`build_world`) and places the enemies (`spawn_enemies`).

## Suggested lesson order
1. **Run the ursina game (`main.py`) first** to get the student excited — it looks like a baby Roblox.
2. **Then build up `raycaster.py`** to teach the real ideas: angles, the game loop, collision, and the raycasting trick.

## How to run

These use the `pygame_env` conda environment.

```bash
conda activate pygame_env

# The pygame raycaster (works right now):
python raycaster.py

# The ursina 3D game (needs one install first):
pip install ursina
python main.py
```

## Controls

**raycaster.py** — W/S move, A/D turn, Q/E strafe, ESC quit
**ursina game (`main.py`)** — mouse look, WASD move, Space jump, Left-click shoot, **R reload**, right-click aim, scroll wheel zoom, ESC quit

> The **arrow keys** also turn the view (`config.KEYBOARD_LOOK`). If your
> mouse can't turn the view at all — some WSL setups can't capture the
> cursor — set `config.MOUSE_LOOK = False` and use the arrow keys.

## The goal of the game
Six red blocks hunt you. Shoot each one three times to kill it; if one gets
next to you it hits you once a second. Kill them all to win — the HUD counts
them down in the top-left corner.

Your magazine holds 12 bullets, and an enemy takes 3, so you *will* have to
reload mid-fight. The blocks on the map stop the enemies walking at you, so
use them as cover while you reload.

## Reloading
```python
MAG_SIZE = 12        # bullets in a magazine
RESERVE_AMMO = 60    # spare bullets you carry
RELOAD_TIME = 1.2    # seconds you are helpless for
AUTO_RELOAD = True   # clicking an empty gun reloads by itself
INFINITE_AMMO = False
```
The HUD shows `magazine / reserve` bottom-right, turning red when empty, with
`RELOADING...` above it while the timer runs.

## Enemies
Everything about them is in `config.py` under `# ----- Enemies -----`:
```python
ENEMY_SPOTS = [(8, 9), (-8, 10), ...]   # where they start — add more!
ENEMY_HEALTH = 3                        # bullets needed to kill one
ENEMY_SPEED = 2                         # slower than you (PLAYER_SPEED = 5)
ENEMY_DAMAGE = 10                       # health you lose per hit
ENEMY_SIGHT_RANGE = 20                  # how close before it notices you
```
How it fits together: a `Bullet` checks its flight path each frame, and if it
hits an `Enemy` it calls `enemy.take_damage()`. At 0 health the enemy calls
`player.add_score()` and deletes itself. The `HUD` never decides anything — it
just reads the player and the enemy list every frame and draws what it sees.

## Switching the gun
The ursina game ships with **two guns**. Open `config.py` and change one line:
```python
GUN_TYPE = "model"   # the downloaded blaster.glb model
GUN_TYPE = "boxes"   # a gun built by hand from cubes
```

## Sound
Four generated sound files: `shoot.wav` (laser "pew"), `reload.wav` (two
clacks), `empty.wav` (the click of an empty gun) and `hit.wav` (the ping when
you hit an enemy). Controlled in `config.py`:
```python
SOUND_ON = True       # turn all sound off/on
SHOOT_VOLUME = 0.5    # 0.0 to 1.0
```
**Note:** WSL has no sound card, so you'll only *hear* it on native Windows — the game still runs fine either way.

## Teaching ideas (easy things to change)
In `raycaster.py`:
- Edit `WORLD_MAP` — draw your own maze with `#` and spaces.
- Change `FOV` to 90 degrees and see the "wider lens" effect.
- Change the wall `color` formula to make blue or green walls.
- Delete the "fish-eye fix" line and watch the walls bend — then put it back!

In the ursina game — **everything fun to change lives in `config.py`**:
- Add more entries to `BLOCK_SPOTS` to build a bigger map.
- Add more entries to `ENEMY_SPOTS` to make a harder fight.
- Change `BLOCK_COLOR` / `BLOCK_TEXTURE` on the blocks.
- Make bullets bigger/faster with `BULLET_SCALE` and `BULLET_SPEED`.
- Shrink `MAG_SIZE` to 3 to feel why reloading matters.
- Set `INFINITE_AMMO = True` for a relaxed "sandbox" mode.
- Slow the mouse down with `MOUSE_SENSITIVITY`.

## Next steps to grow either project
- Make the game restartable instead of "press ESC to quit" on game over.
- Give enemies different sizes/colours/speeds (a fast weak one, a slow tough one).
- Drop an ammo or health pickup where an enemy dies.
- Add textures to the raycaster walls (intermediate).
- Make enemies shoot back.
