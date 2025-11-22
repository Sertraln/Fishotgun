from client.packet.packetstruct import ServerBoundDataPacket,ServerBoundPacket

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

class ServerBoundGameStartPacket(ServerBoundPacket):
    pass

class ServerBoundPlayCardPacket(ServerBoundDataPacket):
    def __init__(self,id:int, pos:int):
        super().__init__(id,pos)
        self.id = id
        self.pos = pos

class ServerBoundShowCardPacket(ServerBoundDataPacket):
    def __init__(self,id:int):
        super().__init__(id)
        self.id = id
    


