from ursina import Entity, Terrain,Vec3, Plane, color, Texture
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletWorld
from panda3d.core import Vec3 as PVec3, NodePath


class WorldScene(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bullet_world = BulletWorld()

from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape
from panda3d.core import Vec3
from panda3d.core import NodePath

world_scene = WorldScene()

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

    body_np = parent.attachNewNode(body)
    body_np.setPos(position)

    bullet_world.attachRigidBody(body)

    return visual, body_np

# Environnement
# ground = Entity(
#     model='cube',
#     scale=(100, 10, 100),
#     texture='grass',
#     texture_scale=(10, 10),
#     collider='box',
#     name='ground',
#     parent=world_scene)

ground = None
water = None

def init_world(base_scene:'NodePath'=None):
    global world_scene
    world_scene.parent = base_scene

    global ground
    ground = Entity(
        model= "assets/models/terrain",
        scale=Vec3(3),
        texture_scale=(10, 10),
        # collider='box',
        # texture=Texture('assets/textures/grass.png'),
        name='ground',
        parent=world_scene)

    Entity(
        model= 'cube',
        position=(0, -1, 0),
        scale=(500, 1, 500),
        # texture_scale=(10, 10),
        #color=color.azure,
        # collider='box',
        name='water',
        parent=world_scene)
    # create_static_box(
    #     bullet_world=world_scene.bullet_world,
    #     parent=world_scene,
    #     position=(0, -5, 0),
    #     scale=(100, 10, 100),
    #     texture='grass',
    #     name='ground'
    # )

    # create_static_box(
    #     bullet_world=world_scene.bullet_world,
    #     parent=world_scene,
    #     position=(5, 9, 15),
    #     scale=(10, 10, 10),
    #     texture='brick',
    #     name='wall'
    # )

    attach_world_bodies(world_scene.bullet_world, base_scene)
    return world_scene

# --- Bullet helpers -------------------------------------------------------
def add_static_box(entity: Entity, bullet_world: BulletWorld, parent_np: NodePath, friction: float = 0.8, mass: float = 0.0):
    """Attach a box-shaped Bullet body matching an Ursina `entity`.

    Returns a tuple (body, body_np) where `body` is the BulletRigidBodyNode and
    `body_np` the NodePath it was attached to.
    """
    if parent_np is None:
        raise ValueError("parent_np (a Panda3D NodePath) is required to attach the Bullet node")

    # Compute half-extents from Ursina scale
    sx, sy, sz = entity.scale
    half_extents = PVec3(sx / 2.0, sy / 2.0, sz / 2.0)

    shape = BulletBoxShape(half_extents)
    body = BulletRigidBodyNode(entity.name or 'static')
    body.setMass(mass)
    body.addShape(shape)
    body.setFriction(friction)

    body_np = parent_np.attachNewNode(body)
    body_np.setPos(entity.position)
    # Try to set orientation if available on the Entity
    try:
        body_np.setHpr(entity.rotation)
    except Exception:
        pass

    bullet_world.attachRigidBody(body)
    return body, body_np


def attach_world_bodies(bullet_world: BulletWorld, parent_np: NodePath, friction: float = 0.8):
    """Attach `ground` and `wall` as static bodies in the given `bullet_world`.

    Returns a dict with keys `'ground'` and `'wall'` mapping to the created NodePaths.
    """

    bodies = {}
    _, bodies['ground'] = add_static_box(ground, bullet_world, parent_np, friction=friction, mass=0.0)
    return bodies