from typing import TYPE_CHECKING

from shared.entity import EntityType
from shared.movement import Physic
from ursina import Vec3
import array
import server.data as data
import struct
from shared.parsedata.vec3data import Vec3Data
if TYPE_CHECKING:
    from server.client import Client

class Player(Physic):
    def __init__(self, player_name: str, client: 'Client',parent=None):
        super().__init__(parent=parent)
        self.type = EntityType.PLAYER
        self.player_name = player_name
        self.client = client
        self.keys_states = None
        self.fish_unlocked = []
        self.load()

    @property
    def id(self) -> int:
        return self.client.id
    
    @property
    def unique_id(self) -> str:
        return self.player_name

    def update_keystates(self, key_states):
        self.keys_states = key_states


    def save(self):
        with open(f"{data.dataPath}{self.unique_id}.dat","wb") as f:
            f.write(Vec3Data.encode(self.position))

    def load(self):
        try:
            with open(f"{data.dataPath}{self.unique_id}.dat","rb") as f:
                self.position = Vec3Data.decode(f.read(Vec3Data.size))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Player load error : {e}")


