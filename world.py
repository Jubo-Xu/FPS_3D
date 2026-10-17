"""
world.py  --  Builds the level: the ground, the blocks, the sky, the enemies.

We keep "building the map" separate from "the game objects" (entities.py)
so that designing the level stays in one easy-to-find place:
  build_world()   -- the scenery (ground, blocks, sky)
  spawn_enemies() -- puts one Enemy on every spot in config.ENEMY_SPOTS
"""
from ursina import Entity
from ursina.prefabs.sky import Sky

import config
from entities import Enemy


def build_world():
    """Create the ground, the blocky obstacles, and the sky."""

    # The floor you walk on. 'collider' lets the player stand on it.
    ground = Entity(
        model="plane",
        scale=config.GROUND_SIZE,
        texture="white_cube",
        texture_scale=(config.GROUND_SIZE, config.GROUND_SIZE),
        color=config.GROUND_COLOR,
        collider="box",
    )

    # Place one block/pillar at every spot listed in config.BLOCK_SPOTS.
    for (x, z) in config.BLOCK_SPOTS:
        Entity(
            model="cube",
            position=(x, 1, z),     # y=1 lifts the block to sit on the ground
            scale=config.BLOCK_SCALE,
            texture=config.BLOCK_TEXTURE,
            color=config.BLOCK_COLOR,
            collider="box",
        )

    # A bright sky so the world doesn't look empty.
    Sky()

    return ground


def spawn_enemies(target):
    """Create one enemy per spot in config.ENEMY_SPOTS.

    `target` is the Player -- every enemy needs to know who to chase.
    We give back the list so the HUD can count how many are left.
    """
    enemies = []
    for (x, z) in config.ENEMY_SPOTS:
        enemies.append(Enemy(position=(x, config.ENEMY_Y, z), target=target))
    return enemies
