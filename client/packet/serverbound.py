import socket
import shared.utils as utils

#client_bound server -> client
#server_bound client -> server

class ServerBoundPacket:
    def get_id(self):
        return serverBoundPacketList.index(self.__class__)

    def send(self,conn:socket.socket):
        conn.send(bytes([serverBoundPacketList.index(self.__class__)]))

class ServerBoundDataPacket(ServerBoundPacket):
    def __init__(self,*data):
        self.data = data

    def send(self, conn):
        packet = utils.parser(self.get_id(),self.data)
        conn.send(packet)

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
    
def getServerBoundPacket(id:int,data:str = "") -> ServerBoundPacket:
    print("client : serverboundget :",data)
    id = data[0]
    packet = serverBoundPacketList[id]
    if issubclass(packet,ServerBoundDataPacket):
       return packet(data)
    else :
        return packet()

serverBoundPacketList = [
    ServerBoundPseudoPacket,
    ServerBoundMessagePacket,
    ServerBoundGameStartPacket,
    ServerBoundPlayCardPacket,
    ServerBoundShowCardPacket
]

# generate the list of packet that need to be parsed
utils.ServerBoundDataPacket = [issubclass(packet,ServerBoundDataPacket) for packet in serverBoundPacketList]
