from typing import TYPE_CHECKING
from server import data
from server.packet.clientbound import ClientBoundSpawnPlayerPacket,ClientBoundPlayerListPacket

if TYPE_CHECKING:
    from server.player import Player
    from server.entity import Entity

class World:
    def __init__(self):
        self.entities : dict[int,'Entity'] = {}
        self.next_entity_id = 0
        self.players : dict[int,'Player'] = {}

    def join_player(self, player:'Player') -> int:
        pid = player.client.id
        
        self.players[pid] = player
        player.client.send(ClientBoundPlayerListPacket(self.players.values()))
        print(f"World: player joined {pid}")
        data.server.broadcast(ClientBoundSpawnPlayerPacket(player),[player.client.id])
        return pid

    def left_player(self, pid:int):
        if pid in self.players:
            del self.players[pid]
            print(f"World: player left {pid}")

    def stop(self):
        for pid, player in list(self.players.items()):
            try:
                player.client.kick()
            except Exception:
                pass
        self.players.clear()

    def add_entity(self, entity:'Entity') -> int:
        entity_id = self.get_next_entity_id()
        self.entities[entity_id] = entity
        entity.id = entity_id
        return entity_id
    
    def get_next_entity_id(self):
        self.next_entity_id += 1
        return self.next_entity_id