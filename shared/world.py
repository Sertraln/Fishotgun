from ursina import Entity, Terrain, Vec3, Plane, color, Texture
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletWorld
from panda3d.core import Vec3 as PVec3, NodePath

world_scene = None

ground = None
water = None


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

    shape = BulletBoxShape(PVec3(scale[0]/2, scale[1]/2, scale[2]/2))
    body = BulletRigidBodyNode(name)
    body.setMass(0.0)
    body.addShape(shape)

    body_np = parent.attachNewNode(body)
    body_np.setPos(position)
    bullet_world.attachRigidBody(body)

    return visual, body_np


def init_world(base_scene: 'NodePath' = None, bullet_world: BulletWorld = None):
    global world_scene, ground, water

    world_scene = base_scene

    ground = Entity(
        model="assets/models/terrain",
        scale=Vec3(3),
        texture_scale=(10, 10),
        name='ground',
        parent=base_scene
    )

    water = Entity(
        model='cube',
        position=(0, -1, 0),
        scale=(500, 1, 500),
        name='water',
        parent=base_scene
    )

    if bullet_world is not None:
        attach_world_bodies(bullet_world, base_scene)

    return world_scene



def add_static_box(
    entity: Entity,
    bullet_world: BulletWorld,
    parent_np: NodePath,
    friction: float = 0.8,
    mass: float = 0.0
):
    if parent_np is None:
        raise ValueError("parent_np est requis pour attacher le noeud Bullet")

    sx, sy, sz = entity.scale
    half_extents = PVec3(sx / 2.0, sy / 2.0, sz / 2.0)

    shape = BulletBoxShape(half_extents)
    body = BulletRigidBodyNode(entity.name or 'static')
    body.setMass(mass)
    body.addShape(shape)
    body.setFriction(friction)

    body_np = parent_np.attachNewNode(body)
    body_np.setPos(entity.position)
    try:
        body_np.setHpr(entity.rotation)
    except Exception:
        pass

    bullet_world.attachRigidBody(body)
    return body, body_np


def attach_world_bodies(bullet_world: BulletWorld, parent_np: NodePath, friction: float = 0.8):
    bodies = {}
    _, bodies['ground'] = add_static_box(ground, bullet_world, parent_np, friction=friction, mass=0.0)

    from panda3d.bullet import BulletPlaneShape
    plane_body = BulletRigidBodyNode('safety_floor')
    plane_body.setMass(0.0)
    plane_body.addShape(BulletPlaneShape(PVec3(0, 0, 1), 0))
    plane_body.setFriction(0.5)
    plane_np = parent_np.attachNewNode(plane_body)
    plane_np.setPos(0, 0, 0)
    bullet_world.attachRigidBody(plane_body)
    bodies['safety_floor'] = plane_np

    return bodies