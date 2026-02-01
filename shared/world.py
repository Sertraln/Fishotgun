from ursina import Entity
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletWorld
from panda3d.core import Vec3 as PVec3, NodePath


class WorldScene(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bullet_world = BulletWorld()

world_scene = WorldScene()

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

def init_world(base_scene:'NodePath'=None):
    global world_scene
    world_scene.parent = base_scene
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
    _, bodies['wall'] = add_static_box(wall, bullet_world, parent_np, friction=friction, mass=0.0)
    return bodies