import socket
from server.packet.packetstruct import ClientBoundDataPacket,ClientBoundPacket,ClientBoundDataListPacket
from typing import TYPE_CHECKING
from typing import Callable

if TYPE_CHECKING:
    from server.player import Player
    from ursina import Vec3

#ClientBound server -> client
#ServerBound client -> server

class ClientBoundIdPacket(ClientBoundPacket):
    def __init__(self,id:int):
        self.id = id

    def send(self,conn:socket.socket):
        conn.send(bytes([self.id]))

class ClientBoundMessagePacket(ClientBoundDataPacket):
    def __init__(self, message:str):
        super().__init__(message)

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

class ClientBoundPlayerPositionPacket(ClientBoundDataPacket):
    def __init__(self, player_id:int, position:'Vec3'):
        super().__init__(player_id,position)
    
