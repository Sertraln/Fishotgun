import socket
from server.packet.packetstruct import ClientBoundDataPacket,ClientBoundPacket,ClientBoundDataListPacket
from typing import TYPE_CHECKING
from shared.parsedata.vec3data import Vec3Data

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
    def __init__(self, message:str):
        super().__init__(message)

class ClientBoundSpawnPlayerPacket(ClientBoundDataPacket):
    def __init__(self, player: 'Player'):
        datas = [
            str(player.id),
            player.player_id,
            Vec3Data.encode(player.position)
        ]
        super().__init__(datas=datas)

class ClientBoundPlayerListPacket(ClientBoundDataListPacket):
    def __init__(self, datas:list['Player']):
        super().__init__(datas)
    
