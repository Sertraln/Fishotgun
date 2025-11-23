from typing import TYPE_CHECKING
from ursina import Vec3
import server.data as data

if TYPE_CHECKING:
    from shared.entity import EntityType

class Entity:
    def __init__(self,enity_type:EntityType,id:int=-1,position:Vec3=Vec3(0,0,0)):
        self.type = enity_type
        self.id = id
        self.position = position
        data.server.world.add_entity(self)