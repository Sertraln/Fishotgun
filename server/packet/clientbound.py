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

class ClientBoundInitPlayerPacket(ClientBoundDataPacket):
    def __init__(self,player:'Player'):
        super().__init__(player.position,player.fish_inventory,player.currency,player.level)
        self.position = player.position
        self.fishunlocked = player.fish_inventory
        self.currency = player.currency
        self.level = player.level

class ClientBoundMessagePacket(ClientBoundDataPacket):
    def __init__(self,origine:str, message:str):
        super().__init__(origine,message)

class ClientBoundSpawnPlayerPacket(ClientBoundDataPacket):
    def __init__(self, player: 'Player'):
        datas = [
            player.id,
            player.player_name,
            player.position,
            player.rotation_y
        ]
        super().__init__(datas=datas)

class ClientBoundPlayerLeavePacket(ClientBoundDataPacket):
    def __init__(self, player_id:int):
        super().__init__(player_id)

class ClientBoundPlayerListPacket(ClientBoundDataListPacket):
    def __init__(self, datas:list['Player']):
        func : Callable[['Player'],list] = lambda player: [player.id,player.player_name,player.position,player.rotation_y]
        super().__init__(datas,func)

class ClientBoundPlayerPositionPacket(ClientBoundDataPacket):
    def __init__(self, player_id:int, position:'Vec3'):
        super().__init__(player_id,position)

class ClientBoundReconcilePositionPacket(ClientBoundDataPacket):
    def __init__(self, timestamp:int, position:'Vec3'):
        super().__init__(timestamp,position)

class ClientBoundAddFishPacket(ClientBoundDataPacket):
    def __init__(self, fish_id:int):
        super().__init__(fish_id)

class ClientBoundClearInventoryPacket(ClientBoundPacket):
    def __init__(self):
        super().__init__()

class ClientBoundFishingSessionPacket(ClientBoundDataPacket):
    def __init__(self, fish_ids: list[int]):
        super().__init__(fish_ids)

class ClientBoundUpdateMoneyPacket(ClientBoundDataPacket):
    def __init__(self, money:int):
        super().__init__(money)

class ClientBoundUpdateLevelPacket(ClientBoundDataPacket):
    def __init__(self, level:int):
        super().__init__(level)