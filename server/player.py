from typing import TYPE_CHECKING

from shared.entity import EntityType
from shared.movement import Physic
from ursina import Vec3
if TYPE_CHECKING:
    from server.client import Client

class Player(Physic):
    def __init__(self, player_name: str, client: 'Client',parent=None):
        super().__init__(parent=parent,position=Vec3(0,0,0))
        self.type = EntityType.PLAYER
        self.player_name = player_name
        self.client = client
        self.keys_states = None

    @property
    def id(self) -> int:
        return self.client.id
    
    def update_keystates(self, key_states):
        self.keys_states = key_states


