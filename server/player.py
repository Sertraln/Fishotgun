from typing import TYPE_CHECKING

from server.entity import Entity
from shared.entity import EntityType
from shared.parser import Parser
from shared.parsedata.vec3data import Vec3Data

if TYPE_CHECKING:
    from server.client import Client

class Player(Entity,Parser):
    def __init__(self, player_name:str, client: 'Client'):
        Entity.__init__(EntityType.PLAYER,0)
        self.player_id = player_name
        self.client = client
        self.position = (0,0,0)


