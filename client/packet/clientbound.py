from client.packet.packetstruct import ClientBoundPacket,ClientBoundDataPacket
from ursina import Vec3
from shared.parsedata.vec3data import Vec3Data
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
    def __init__(self,data:list[str]):
        super().__init__(data)

    def handle(self):
        pass

class ClientBoundSpawnPlayerPacket(ClientBoundDataPacket):
    def __init__(self,data:list[str]):
        a = bytes("test","utf-8")[0]
        super().__init__(data)
        self.id = int(data[0])
        self.name = data[1]
        self.position = Vec3Data.decode(data[2])

    def handle(self):
        #TODO spawn player entity
        pass