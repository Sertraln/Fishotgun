import os
import sys

if __name__ == "__main__":
    # Ensure project root is on sys.path so sibling packages like `shared` can be imported
    _ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

import server.packet.clientbound as cb
from server.packet.packetstruct import ServerBoundDataPacket,ServerBoundPacket
from typing import TYPE_CHECKING
from shared.movement import Physic

if TYPE_CHECKING:
    from server.client import Client
    from shared.parsedata.input import KeyStates

#client_bound server -> client
#server_bound client -> server

class ServerBoundPseudoPacket(ServerBoundDataPacket):
    def __init__(self,data:list):
        super().__init__(data)
        self.name = data[0]

class ServerBoundMessagePacket(ServerBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)
        self.message = data[0]

    def handle(self, client : 'Client'):
        print("server : message get :",self.message, flush=True)
        player = client.server.world.players.get(client.id)
        if player != None:
            client.server.broadcast(cb.ClientBoundMessagePacket(player.player_name,self.message))

class ServerBoundMovementPacket(ServerBoundDataPacket):
    def __init__(self,data:list['KeyStates',int]):
        super().__init__(data)
        self.key_states: KeyStates = data[0]
        self.timestamp: int = data[1]

    def handle(self, client : 'Client'):
        client.server.world.update_player_movement(client, self.key_states, self.timestamp)

class ServerBoundRotationPacket(ServerBoundDataPacket):
    def __init__(self,data:list[float,int]):
        super().__init__(data)
        self.rotation: float = data[0]
        self.timestamp: int = data[1]

    def handle(self, client : 'Client'):
        client.server.world.update_player_rotation(client, self.rotation, self.timestamp)

if __name__ == "__main__":
    from shared.loadfile import get_defined_classes
    print(issubclass(get_defined_classes("server/packet/serverbound.py")[0],ServerBoundDataPacket))

class ServerBoundRequestFishingPacket(ServerBoundDataPacket):
    def __init__(self, data: list):
        super().__init__(data)

    def handle(self, client: 'Client'):
        from server.fishing_manager import generate_fishing_pool
        fish_ids = generate_fishing_pool()
        client.send(cb.ClientBoundFishingSessionPacket(fish_ids))

class ServerBoundCatchFishPacket(ServerBoundDataPacket):
    def __init__(self, data: list):
        super().__init__(data)

    def handle(self, client: 'Client'):
        if client.player:
            from shared.registry import fish_list
            fish_id = self.data[0]
            
            if 0 <= fish_id < len(fish_list):
                fish_data = fish_list[fish_id]
                client.player.add_fish(fish_data.fishid, 1)
                client.player.save()