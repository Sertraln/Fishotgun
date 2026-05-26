from typing import TYPE_CHECKING
import struct

from shared.entity import EntityType
from shared.movement import Physic
from ursina import Vec3
import server.data as data
from shared.parsedata.vec3data import Vec3Data
from shared.parsedata.fishlist import FishInventory, FishList
from server.packet.clientbound import ClientBoundAddFishPacket, ClientBoundClearInventoryPacket,ClientBoundUpdateMoneyPacket,ClientBoundUpdateLevelPacket
if TYPE_CHECKING:
    from server.client import Client
    from shared.registry import FishData

class Player(Physic):
    def __init__(self, player_name: str, client: 'Client', parent=None):
        super().__init__(parent=parent)
        self.type = EntityType.PLAYER
        self.player_name = player_name
        self.client = client
        self.keys_states = None
        self.fish_inventory = FishInventory()
        self._currency: int = 0
        self.position = Vec3(0, 0, 0)
        self._level = 0
        self.load()

    @property
    def level(self) -> int:
        return self._level
    
    @level.setter
    def level(self, value: int):
        self._level = value
        self.client.send(ClientBoundUpdateLevelPacket(self._level)) 

    @property
    def currency(self) -> int:
        return self._currency

    @currency.setter
    def currency(self, value: int):
        self._currency = value
        self.client.send(ClientBoundUpdateMoneyPacket(self._currency))

    @property
    def id(self) -> int:
        return self.client.id
    
    @property
    def unique_id(self) -> str:
        ip_addr = self.client.ip[0] if isinstance(self.client.ip, tuple) else self.client.ip
        return f"{self.player_name}_{ip_addr}"

    def update_keystates(self, key_states):
        self.keys_states = key_states

    def get_total_fish_count(self) -> int:
        return sum(self.fish_inventory.capacity)

    def save(self):
        try:
            with open(f"{data.dataPath}{self.unique_id}.dat", "wb") as f:
                f.write(Vec3Data.encode(self.position))
                f.write(FishInventory.encode(self.fish_inventory))
                f.write(self.currency.to_bytes(4))
                f.write(self.level.to_bytes(2))
            print(f"Serveur : Profil sauvegardé pour ID {self.unique_id}")
        except Exception as e:
            print(f"Serveur : Erreur sauvegarde {self.unique_id} : {e}")

    def load(self):
        path = f"{data.dataPath}{self.unique_id}.dat"
        try:
            with open(path, "rb") as f:
                # On lit séquentiellement dans l'ordre de la sauvegarde
                self.position = Vec3Data.decode(f.read(Vec3Data.size))
                self.fish_inventory = FishInventory.decode(f.read(FishInventory.size))
                self.currency = int.from_bytes(f.read(4))
                self.level = int.from_bytes(f.read(2))
                    
            print(f"Serveur : Profil chargé pour ID {self.unique_id}")
        except FileNotFoundError:
            print(f"Serveur : Nouveau profil créé pour {self.unique_id}")
            self.fish_inventory = FishInventory()
            self.currency = 0
        except Exception as e:
            print(f"Serveur : Erreur chargement {self.unique_id} : {e}")
            self.fish_inventory = FishInventory()

    def add_fish(self, fish: FishList, quantity: int = 1):
        print(f"Player {self.unique_id} : Ajout de {quantity} x {fish.name}")
        self.fish_inventory.add_fish(fish, quantity)
        self.client.send(ClientBoundAddFishPacket(fish))

    def clear_inventory(self):
        self.fish_inventory.clear_inventory()
        self.client.send(ClientBoundClearInventoryPacket())