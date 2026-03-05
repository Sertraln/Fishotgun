from client.packet.packetstruct import ClientBoundPacket,ClientBoundDataPacket
from ursina import Vec3
import client.data as data
#client_bound server -> client
#server_bound client -> server

class ClientBoundIdPacket(ClientBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)
        self.id = int(data[0])

    def handle(self):
        pass

class ClientBoundMessagePacket(ClientBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)
        self.message = self.data[0]

    def handle(self):
        #TODO l.chat.addMessage(self.message)
        pass

class ClientBoundPlayerListPacket(ClientBoundDataPacket):
    def __init__(self,data:list[list[int | str | Vec3]]):
        super().__init__(data)

    def handle(self):
        print("client : player list get :",self.data, flush=True)
        for player_data in self.data:
            player_id : int = player_data[0]
            name : str = player_data[1]
            position : Vec3 = player_data[2]
            data.world.spawn_player(player_id,name,position)

class ClientBoundSpawnPlayerPacket(ClientBoundDataPacket):
    def __init__(self,data:list[int | str | Vec3]):
        super().__init__(data)
        self.player_id : int = data[0]
        self.name : str = data[1]
        self.position : Vec3 = data[2]

    def handle(self):
        data.world.spawn_player(self.player_id,self.name,self.position)

class ClientBoundPlayerLeavePacket(ClientBoundDataPacket):
    def __init__(self,data:list[int]):
        super().__init__(data)
        self.player_id : int = data[0]

    def handle(self):
        print("client : player leave get :",self.player_id, flush=True)
        if self.player_id in data.world.players:
            del data.world.players[self.player_id]

class ClientBoundPlayerPositionPacket(ClientBoundDataPacket):
    def __init__(self,data:list):
        super().__init__(data)
        self.player_id : int = data[0]
        self.position : Vec3 = data[1]

    def handle(self):
        print("client : player position get :",self.player_id,self.position, flush=True)
        data.world.players[self.player_id].position = self.position

class ClientBoundRotationPacket(ClientBoundDataPacket):
    def __init__(self,data:list):
        super().__init__(data)
        self.player_id : int = data[0]
        self.rotation : Vec3 = data[1]

    def handle(self):
        print("client : player rotation get :",self.player_id,self.rotation, flush=True)
        data.world.players[self.player_id].rotation = self.rotation