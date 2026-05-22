from typing import TYPE_CHECKING

from shared.entity import EntityType
from shared.movement import Physic
from ursina import Vec3
import server.data as data
from shared.parsedata.vec3data import Vec3Data
from shared.parsedata.fishlist import FishInventory
from server.packet.clientbound import ClientBoundAddFishPacket, ClientBoundClearInventoryPacket
if TYPE_CHECKING:
    from server.client import Client

class Player(Physic):
    def __init__(self, player_name: str, client: 'Client',parent=None):
        super().__init__(parent=parent)
        self.type = EntityType.PLAYER
        self.player_name = player_name
        self.client = client
        self.keys_states = None
        self.fish_inventory = FishInventory()
        self.load()

    @property
    def id(self) -> int:
        return self.client.id
    
    @property
    def unique_id(self) -> str:
        return self.player_name+"_"+str(self.client.ip[0])

    def update_keystates(self, key_states):
        self.keys_states = key_states

    def save(self):
        with open(f"{data.dataPath}{self.unique_id}.dat","wb") as f:
            f.write(Vec3Data.encode(self.position))
            f.write(FishInventory.encode(self.fish_inventory))

    def load(self):
        try:
            with open(f"{data.dataPath}{self.unique_id}.dat","rb") as f:
                self.position = Vec3Data.decode(f.read(Vec3Data.size))
                self.fish_inventory = FishInventory.decode(f.read(FishInventory.size))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Player load error : {e}")

    def add_fish(self, fish:FishInventory):
        self.fish_inventory.add_fish(fish)
        self.client.conn.send(ClientBoundAddFishPacket(fish))

    def clear_inventory(self):
        self.fish_inventory = FishInventory()
        self.client.conn.send(ClientBoundClearInventoryPacket())
