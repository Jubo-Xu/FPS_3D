import os
# --- WSL / no-GPU fix: use software (CPU) rendering when there's no graphics
#     card, so the 3D window doesn't open black. Harmless on a normal PC.
#     MUST come before importing ursina. ---
if not os.path.exists('/dev/dri'):
    os.environ.setdefault('LIBGL_ALWAYS_SOFTWARE', '1')
    os.environ.setdefault('GALLIUM_DRIVER', 'llvmpipe')

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()
window.title = 'My First 3D FPS'
window.size = (960, 540)
window.fullscreen = False
window.borderless = False

ground = Entity(model='plane', scale=32, texture='white_cube',
                texture_scale=(32, 32), color=color.green.tint(-0.3),
                collider='box')
Sky()

# NEW: walk (WASD) + look (mouse) + jump (space), all built in
player = FirstPersonController(y=2, origin_y=-0.5, speed=5,
                              mouse_sensitivity=Vec2(20, 20))
player.cursor.enabled = False   # hide the default pink dot
app.run()