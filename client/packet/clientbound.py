from client.packet.packetstruct import ClientBoundPacket,ClientBoundDataPacket
from ursina import Vec3
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
        print("player list :",self.data)
        pass

class ClientBoundSpawnPlayerPacket(ClientBoundDataPacket):
    def __init__(self,data:list):
        super().__init__(data)
        self.player_id : int = data[0]
        self.name : str = data[1]
        self.position : Vec3 = data[2]

    def handle(self):
        print(f"Spawn player {self.name} at {self.position}")
        #TODO spawn player entity
        pass

class ClientBoundPlayerPositionPacket(ClientBoundDataPacket):
    def __init__(self,data:list):
        super().__init__(data)
        self.player_id : int = data[0]
        self.position : Vec3 = data[1]

    def handle(self):
        print(f"Update player {self.player_id} position to {self.position}")
        #TODO update player position
        pass