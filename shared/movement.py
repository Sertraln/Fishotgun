from ursina import Vec3,Entity,boxcast,Vec2,CapsuleCollider,raycast
from ursina.scene import Scene
from panda3d.core import NodePath
from panda3d.physics import ForceNode,LinearVectorForce
from shared.parsedata.input import KeyStates

from ursina import Vec3,Entity

class Physic(Entity):
    def __init__(self):
        super().__init__()
        self.height: float = 2
        self.radius: float = 0.5
        self.center: Vec3 = Vec3(self.position.x, self.position.y + self.height / 2, self.position.z)
        self.acceleration: Vec3 = Vec3(0, 0, 0)
        self.vitesse: Vec3 = Vec3(0, 0, 0)
        self.jump_height: float = 0.3
        self.gravity: float = -0.6
        self.air_time: float = 0
        self.grounded = False
        self.ignore_list = [self]
        self.speed:float = 1

    def _calculate_speed(self,key_strokes:KeyStates):
        if key_strokes.is_pressed(KeyStates.SPRINT):
            return 1.6
        else:
            return 1.0

from shared.world import world_scene as colliders_to_test

def update_pos(player:Physic,dt:float, key_strokes:KeyStates):
    pass