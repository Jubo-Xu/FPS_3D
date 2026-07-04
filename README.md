# 3D FPS starters (for teaching)

Two ways to make a first-person shooter in Python, from the same folder.

| What | Files | Best for |
|------|-----------|----------|
| **Real 3D FPS** (ursina engine) | `main.py` + `config.py` + `entities.py` + `world.py` | The "wow, I made a real game!" hook. Run `main.py`. |
| **Raycaster** (pure pygame) | `raycaster.py` | Teaching how 3D *actually* works. No engine — we fake 3D with math. |

### The ursina project files
- **`main.py`** — the file you run. Wires everything together and starts the game.
- **`config.py`** — every tweakable number (speed, gun, map...) in one place.
- **`entities.py`** — the `Player`, `Gun`, `Bullet`, `Crosshair` classes.
- **`world.py`** — builds the level (ground, blocks, sky).

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
**ursina game (`main.py`)** — mouse look, WASD move, Space jump, Left-click shoot, ESC quit

## Switching the gun
The ursina game ships with **two guns**. Open `config.py` and change one line:
```python
GUN_TYPE = "model"   # the downloaded blaster.glb model
GUN_TYPE = "boxes"   # a gun built by hand from cubes
```

## Sound
Clicking to shoot plays `shoot.wav` (a generated laser "pew"). Controlled in `config.py`:
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
- Change `BLOCK_COLOR` / `BLOCK_TEXTURE` on the blocks.
- Make bullets bigger/faster with `BULLET_SCALE` and `BULLET_SPEED`.
- Slow the mouse down with `MOUSE_SENSITIVITY`.

## Next steps to grow either project
- Add enemy targets and detect hits.
- Add a score counter and a simple HUD.
- Add textures to the raycaster walls (intermediate).
- Add sound effects on shooting.
