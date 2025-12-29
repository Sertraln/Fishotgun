from enum import Enum

class EntityType(Enum):
    PLAYER = 1
    NPC = 2
    
from ursina import Vec3,Entity

class Colider(Entity):
    def __init__(self, position: Vec3, height: float, radius: float):
        self.position: Vec3 = position
        self.height: float = height
        self.radius: float = radius
        self.center: Vec3 = Vec3(position.x, position.y + height / 2, position.z)