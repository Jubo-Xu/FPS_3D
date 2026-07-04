"""
world.py  --  Builds the level: the ground, the blocks, and the sky.

We keep "building the map" separate from "the game objects" (entities.py)
so that designing the level stays in one easy-to-find place.
"""
from ursina import Entity
from ursina.prefabs.sky import Sky

import config


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
