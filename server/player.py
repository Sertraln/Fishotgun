from typing import TYPE_CHECKING

from server.entity import Entity
from shared.entity import EntityType
from ursina import Vec3

if TYPE_CHECKING:
    from server.client import Client

class Player(Entity):
    def __init__(self, player_name:str, client: 'Client'):
        super().__init__(EntityType.PLAYER,client.id)
        self.player_id = player_name
        self.client = client
        self.position = Vec3()


