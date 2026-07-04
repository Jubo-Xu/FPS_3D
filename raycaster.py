"""
========================================================================
  SIMPLE 3D FPS in pygame  --  "Raycasting" (the Wolfenstein 3D trick)
========================================================================

HOW DOES THIS WORK?  (read this first!)
---------------------------------------
pygame can only draw FLAT 2D shapes. So how do we get a 3D world?

We cheat -- in a very clever way that real games used in the 1990s:

1. The map is just a 2D grid (like graph paper). 1 = wall, 0 = empty.
2. The player stands somewhere on the grid and faces a direction (an angle).
3. For EVERY vertical column of pixels on the screen, we shoot an
   imaginary "ray" out from the player into the map until it hits a wall.
4. The FARTHER the wall is, the SHORTER we draw that column.
   The CLOSER the wall is, the TALLER we draw it.
5. Do this for all ~120 columns and your brain sees a 3D hallway!

That's the whole idea. It's just trigonometry + drawing vertical lines.

CONTROLS
--------
  W / S .... move forward / backward
  A / D .... turn left / right
  Q / E .... step (strafe) left / right
  ESC ...... quit

Run it with:   python raycaster.py
"""

import math
import pygame

# ----------------------------------------------------------------------
# 1) SETTINGS  -- change these numbers to experiment!
# ----------------------------------------------------------------------
SCREEN_WIDTH = 800        # window width in pixels
SCREEN_HEIGHT = 500       # window height in pixels
FPS = 60                  # frames per second (how often we redraw)

# The map. Each character is one square of the world.
# '#' is a wall, ' ' (space) is empty floor you can walk on.
# The map is drawn here exactly how it looks from above (a top-down view).
WORLD_MAP = [
    "########",
    "#      #",
    "#  ##  #",
    "#  ##  #",
    "#      #",
    "#    # #",
    "#      #",
    "########",
]
MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)

# Player starting position. These are in "map squares", and they can be
# decimals (2.5 means halfway across square number 2).
player_x = 3.5
player_y = 4.5
player_angle = 0.0        # which way the player is looking, in radians

# How wide the player's view is (Field Of View). 60 degrees feels natural.
FOV = math.radians(60)

# We don't shoot a ray for every single pixel column (that's a lot!).
# Instead we shoot one ray every few pixels to keep it fast and smooth.
RAY_COUNT = 240                          # number of rays across the screen
COLUMN_WIDTH = SCREEN_WIDTH / RAY_COUNT   # how wide each wall slice is

MAX_DEPTH = 16            # how far a ray is allowed to travel before giving up

MOVE_SPEED = 3.0          # squares per second
TURN_SPEED = 2.5          # radians per second

# Some colors (Red, Green, Blue -- each from 0 to 255)
CEILING_COLOR = (40, 40, 60)     # dark blue-ish sky
FLOOR_COLOR = (60, 50, 40)       # brownish ground


# ----------------------------------------------------------------------
# 2) HELPER: is a given map square a wall?
# ----------------------------------------------------------------------
def is_wall(x, y):
    """Return True if the map square at (x, y) is a wall '#'."""
    # If we're outside the map, treat it as a wall (so you can't escape).
    if x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT:
        return True
    # int(x) turns 3.7 into 3 -- we need the whole-number grid square.
    return WORLD_MAP[int(y)][int(x)] == "#"


# ----------------------------------------------------------------------
# 3) THE RAYCASTER -- this is the heart of the 3D effect
# ----------------------------------------------------------------------
def cast_rays(screen):
    """Shoot rays across the screen and draw the walls we hit."""

    # The leftmost ray points a bit to the player's left, the rightmost a
    # bit to the right. We sweep from one side of the FOV to the other.
    for ray in range(RAY_COUNT):

        # Work out the exact angle of THIS ray.
        # ray_screen goes from -0.5 (far left) to +0.5 (far right).
        ray_screen = (ray / RAY_COUNT) - 0.5
        ray_angle = player_angle + ray_screen * FOV

        # The direction the ray travels, broken into x and y parts.
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)

        # March the ray forward in tiny steps until it hits a wall.
        # (This "step a little, check, repeat" method is simple to read.
        #  Real engines use a faster method called DDA, but this is clearer.)
        distance = 0.0
        step = 0.02
        hit = False
        while distance < MAX_DEPTH and not hit:
            distance += step
            test_x = player_x + ray_dir_x * distance
            test_y = player_y + ray_dir_y * distance
            if is_wall(test_x, test_y):
                hit = True

        # ----- FISH-EYE FIX -----
        # If we used the raw distance, straight walls would look curved
        # (like a fish-eye lens). Multiplying by cos() of the ray's offset
        # angle flattens them back out. This one line is a classic trick!
        corrected = distance * math.cos(ray_screen * FOV)

        # ----- TURN DISTANCE INTO WALL HEIGHT -----
        # Close wall (small distance) -> tall slice.
        # Far wall   (big distance)   -> short slice.
        if corrected < 0.0001:
            corrected = 0.0001   # avoid dividing by zero
        wall_height = int(SCREEN_HEIGHT / corrected)

        # Find the top and bottom y-positions of this wall slice,
        # centered vertically on the screen.
        wall_top = SCREEN_HEIGHT // 2 - wall_height // 2
        wall_bottom = SCREEN_HEIGHT // 2 + wall_height // 2

        # ----- SHADING -----
        # Make far walls darker so depth is easier to see.
        shade = max(0, 255 - int(corrected * 25))
        color = (shade, shade // 2, shade // 3)  # a warm orange-ish wall

        # ----- DRAW THE WALL SLICE -----
        x = int(ray * COLUMN_WIDTH)
        pygame.draw.rect(
            screen, color,
            (x, wall_top, math.ceil(COLUMN_WIDTH), wall_bottom - wall_top)
        )


# ----------------------------------------------------------------------
# 4) DRAW A SIMPLE CROSSHAIR (the FPS aiming dot)
# ----------------------------------------------------------------------
def draw_crosshair(screen):
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    pygame.draw.line(screen, (255, 255, 255), (cx - 10, cy), (cx + 10, cy), 2)
    pygame.draw.line(screen, (255, 255, 255), (cx, cy - 10), (cx, cy + 10), 2)


# ----------------------------------------------------------------------
# 5) MAIN PROGRAM -- set up the window and run the game loop
# ----------------------------------------------------------------------
def main():
    global player_x, player_y, player_angle   # we change these as we play

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("My First 3D FPS - pygame raycaster")
    clock = pygame.time.Clock()

    running = True
    while running:
        # dt = "delta time": how many seconds the last frame took.
        # We multiply movement by dt so the game runs the same speed on
        # any computer, fast or slow.
        dt = clock.tick(FPS) / 1000.0

        # ----- HANDLE EVENTS (like closing the window) -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # ----- READ THE KEYBOARD (held-down keys) -----
        keys = pygame.key.get_pressed()

        # Turning left / right changes the angle we are facing.
        if keys[pygame.K_a]:
            player_angle -= TURN_SPEED * dt
        if keys[pygame.K_d]:
            player_angle += TURN_SPEED * dt

        # Work out the "forward" direction from our angle.
        forward_x = math.cos(player_angle)
        forward_y = math.sin(player_angle)
        # "Strafe" direction is 90 degrees to the side of forward.
        strafe_x = math.cos(player_angle + math.pi / 2)
        strafe_y = math.sin(player_angle + math.pi / 2)

        # Figure out where the player WANTS to move this frame.
        move_x = 0.0
        move_y = 0.0
        if keys[pygame.K_w]:
            move_x += forward_x * MOVE_SPEED * dt
            move_y += forward_y * MOVE_SPEED * dt
        if keys[pygame.K_s]:
            move_x -= forward_x * MOVE_SPEED * dt
            move_y -= forward_y * MOVE_SPEED * dt
        if keys[pygame.K_e]:
            move_x += strafe_x * MOVE_SPEED * dt
            move_y += strafe_y * MOVE_SPEED * dt
        if keys[pygame.K_q]:
            move_x -= strafe_x * MOVE_SPEED * dt
            move_y -= strafe_y * MOVE_SPEED * dt

        # ----- COLLISION: don't walk through walls -----
        # We check the x and y moves separately so you can "slide" along
        # a wall instead of getting completely stuck on it.
        if not is_wall(player_x + move_x, player_y):
            player_x += move_x
        if not is_wall(player_x, player_y + move_y):
            player_y += move_y

        # ----- DRAW EVERYTHING -----
        # First paint the ceiling (top half) and floor (bottom half).
        screen.fill(CEILING_COLOR)
        pygame.draw.rect(
            screen, FLOOR_COLOR,
            (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        )

        # Then draw the 3D walls on top, and the crosshair last.
        cast_rays(screen)
        draw_crosshair(screen)

        # Show the finished frame on the monitor.
        pygame.display.flip()

    pygame.quit()


# This line means: only run the game if we launched THIS file directly.
if __name__ == "__main__":
    main()
