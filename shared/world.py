from ursina import Entity, Terrain, Vec3, Plane, color, Texture
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletWorld
from panda3d.core import Vec3 as PVec3, NodePath
from direct.actor.Actor import Actor
import csv
import os

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

def get_shopkeeper():
    global shopkeeper
    return shopkeeper

def init_world(base_scene:'NodePath'=None):
    global world_scene
    world_scene.parent = base_scene

    spawn_trees()

    global ground
    ground = Entity(
        model= "assets/models/terrain.obj",
        scale=Vec3(3),
        texture_scale=(10, 10),
        # collider='box',
        # texture=Texture('assets/textures/grass.png'),
        name='ground',
        parent=world_scene)

    global water
    water=Entity(
        model= 'cube',
        position=(0, -1, 0),
        scale=(500, 1, 500),
        # texture_scale=(10, 10),
        #color=color.azure,
        # collider='box',
        name='water',
        parent=world_scene)
    
    global shop_building, shopkeeper

    shop_building = Entity(
        model='assets/models/Shop.glb',
        position=(28, 2.3, -10),
        rotation=(0, 270, 0),
        scale=1,
        collider='mesh',
        name='shop_building',
        parent=world_scene
    )

    shopkeeper = Actor('assets/models/Shopkeeper.glb')

    shopkeeper.reparent_to(world_scene)
    shopkeeper.set_pos(27, 0.2, -10)
    shopkeeper.set_hpr(90, 360, 0)
    shopkeeper.set_scale(1.2)
    shopkeeper.name = 'shopkeeper'
    shopkeeper.loop('idle')

    attach_world_bodies(world_scene.bullet_world, base_scene)
    return world_scene

scale_factor = 3

def spawn_trees():
    _ROOT = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(_ROOT, 'shared', 'data', 'trees.csv')
    
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier est introuvable à : {file_path}")
        return

    with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                Entity(
                    model='assets/models/tree.glb',
                    position=(-float(row['x'])*scale_factor, 2.4668*2, -float(row['y'])*scale_factor),
                    rotation_y=float(row['rotation_z_deg']),
                    scale=2,
                    collider='box',
                    parent=world_scene
                )
    print("Arbres chargés avec succès !")

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