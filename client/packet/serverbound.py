from client.packet.packetstruct import ServerBoundDataPacket,ServerBoundPacket
from shared.parsedata.input import KeyStates

#client_bound server -> client
#server_bound client -> server

class ServerBoundPseudoPacket(ServerBoundDataPacket):
    def __init__(self,pseudo:str):
        super().__init__(pseudo)
        self.name = pseudo

class ServerBoundMessagePacket(ServerBoundDataPacket):
    def __init__(self,data:str):
        super().__init__(data)
        self.message = data
    
class ServerBoundMovementPacket(ServerBoundDataPacket):
    def __init__(self, key_states:KeyStates, timestamp:int):
        self.key_states = key_states
        self.timestamp = timestamp
        super().__init__(key_states, timestamp)

class ServerBoundRotationPacket(ServerBoundDataPacket):
    def __init__(self,rotation:float,timestamp:int):
        self.rotation = rotation
        self.timestamp = timestamp
        super().__init__(rotation, timestamp)