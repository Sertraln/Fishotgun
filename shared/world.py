from ursina import Entity
world_scene = Entity()

# Environnement
ground = Entity(
    parent=world_scene,
    model='cube',
    scale=(100, 10, 100),
    texture='grass',
    texture_scale=(10, 10),
    name='ground')

wall = Entity(
    parent=world_scene,
    model='cube',
    scale=(10, 10, 10),
    position=(5, 9, 15),
    texture='brick',
    name='wall')

def init_world(base_scene:'Scene'=None):
    global world_scene
    world_scene.parent = base_scene
    return world_scene