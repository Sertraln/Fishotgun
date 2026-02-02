from ursina import Entity
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape
from panda3d.core import Vec3
from panda3d.core import NodePath

world_scene = Entity()

def create_static_box(
    bullet_world,
    parent,
    position=(0, 0, 0),
    scale=(1, 1, 1),
    texture=None,
    name="static"
):

    visual = Entity(
        parent=parent,
        model='cube',
        position=position,
        scale=scale,
        texture=texture,
        name=name
    )

    shape = BulletBoxShape(Vec3(scale[0]/2, scale[1]/2, scale[2]/2))
    body = BulletRigidBodyNode(name)
    body.setMass(0.0)
    body.addShape(shape)

    body_np = render.attachNewNode(body)
    body_np.setPos(position)

    bullet_world.attachRigidBody(body)

    return visual, body_np


def init_world(bullet_world, base_scene=None):
    global world_scene
    world_scene.parent = base_scene

    create_static_box(
        bullet_world=bullet_world,
        parent=world_scene,
        position=(0, -5, 0),
        scale=(100, 10, 100),
        texture='grass',
        name='ground'
    )

    create_static_box(
        bullet_world=bullet_world,
        parent=world_scene,
        position=(5, 9, 15),
        scale=(10, 10, 10),
        texture='brick',
        name='wall'
    )

    return world_scene