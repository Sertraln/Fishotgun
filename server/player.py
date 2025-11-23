from typing import TYPE_CHECKING

from server.entity import Entity,EntityType

if TYPE_CHECKING:
    from server.client import Client

class Player(Entity):
    def __init__(self, player_name:str, client: 'Client'):
        super().__init__(EntityType.PLAYER,0)
        self.player_id = player_name
        self.client = client
        self.position = (0,0,0)

