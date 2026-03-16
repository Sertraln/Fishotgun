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

if TYPE_CHECKING:
    from server.client import Client
    from shared.parsedata.input import KeyStates

#client_bound server -> client
#server_bound client -> server

class ServerBoundPseudoPacket(ServerBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)
        print(data)
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
        #TODO handle movement
        pass

if __name__ == "__main__":
    from shared.loadfile import get_defined_classes
    print(issubclass(get_defined_classes("server/packet/serverbound.py")[0],ServerBoundDataPacket))