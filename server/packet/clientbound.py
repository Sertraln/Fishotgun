import socket
from server.packet.packetstruct import ClientBoundDataPacket,ClientBoundPacket,ClientBoundDataListPacket
from typing import TYPE_CHECKING
from typing import Callable

if TYPE_CHECKING:
    from server.player import Player

#ClientBound server -> client
#ServerBound client -> server

class ClientBoundIdPacket(ClientBoundPacket):
    def __init__(self,id:int):
        self.id = id

    def send(self,conn:socket.socket):
        conn.send(bytes([self.id]))

class ClientBoundMessagePacket(ClientBoundDataPacket):
    def __init__(self,origine:str, message:str):
        super().__init__(origine,message)

class ClientBoundSpawnPlayerPacket(ClientBoundDataPacket):
    def __init__(self, player: 'Player'):
        datas = [
            player.id,
            player.player_name,
            player.position
        ]
        super().__init__(datas=datas)

class ClientBoundPlayerListPacket(ClientBoundDataListPacket):
    def __init__(self, datas:list['Player']):
        func : Callable[['Player'],list] = lambda player: [player.id,player.player_name,player.position]
        super().__init__(datas,func)
    
