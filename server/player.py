from typing import TYPE_CHECKING
from shared.entity import EntityType
from shared.movement import Physic
from ursina import Vec3
import server.data as data
from shared.parsedata.vec3data import Vec3Data
from panda3d.core import NodePath

if TYPE_CHECKING:
    from server.client import Client

class Player:
    def __init__(self, player_name: str, client: 'Client', parent=None):
        self._physic = Physic(
            parent=NodePath("player_root"),
            bullet_world=data.server.world.bullet_world
        )
        self.type = EntityType.PLAYER
        self.player_name = player_name
        self.client = client
        self.keys_states = None
        self.fish_unlocked = []
        self.rotation_y = 0.0
        self.load()

    @property
    def position(self) -> Vec3:
        return self._physic.position

    @position.setter
    def position(self, value: Vec3):
        self._physic.set_position(value)

    @property
    def id(self) -> int:
        return self.client.id

    @property
    def unique_id(self) -> str:
        return self.player_name + "_" + str(self.client.ip[0])

    def update_keystates(self, key_states):
        self.keys_states = key_states

    def update_phy(self, dt: float, key_states):
        self._physic.rotation_y = self.rotation_y
        self._physic.update_phy(dt, key_states)

    def save(self):
        with open(f"{data.dataPath}{self.unique_id}.dat", "wb") as f:
            f.write(Vec3Data.encode(self.position))

    def load(self):
        try:
            with open(f"{data.dataPath}{self.unique_id}.dat", "rb") as f:
                self.position = Vec3Data.decode(f.read(Vec3Data.size))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Player load error : {e}")