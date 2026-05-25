from client.packet.packetstruct import ServerBoundDataPacket,ServerBoundPacket
from shared.parsedata.input import KeyStates
from ursina import Vec3

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
        super().__init__(key_states, timestamp)
        self.key_states = key_states
        self.timestamp = timestamp

class ServerBoundRotationPacket(ServerBoundDataPacket):
    def __init__(self,rotation:float,timestamp:int):
        super().__init__(rotation, timestamp)
        self.rotation : float = rotation
        self.timestamp : int = timestamp

class ServerBoundRequestFishingPacket(ServerBoundDataPacket):
    def __init__(self, dummy: int = 0):
        super().__init__(dummy)

class ServerBoundCatchFishPacket(ServerBoundDataPacket):
    def __init__(self, fish_id: int):
        super().__init__(fish_id)
        self.fish_id = fish_id