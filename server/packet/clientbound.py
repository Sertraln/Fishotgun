import socket
import shared.utils as utils

#ClientBound server -> client
#ServerBound client -> server

class ClientBoundPacket:
    def get_id(self):
        return clientBoundPacketList.index(self.__class__)
    
    def send(self,conn:socket.socket):
        conn.send(bytes([clientBoundPacketList.index(self.__class__)]))

class ClientBoundDataPacket(ClientBoundPacket):
    def __init__(self,*data:str,datas:list[str] = None ):
        if datas is not None:
            self.data = datas
        else:
            self.data = data

    def send(self, conn):
        packet = utils.parser(self.get_id(),self.data)
        conn.send(packet)

class ClientBoundDataListPacket(ClientBoundDataPacket):
    def __init__(self,datas:list):
        endode_datas = []
        for data in datas:
            endode_datas.append(data.encode())
        super().__init__(datas=endode_datas)

class ClientBoundIdPacket(ClientBoundPacket):
    def __init__(self,id:int):
        self.id = id

    def send(self,conn:socket.socket):
        conn.send(bytes([self.id]))

class ClientBoundMessagePacket(ClientBoundDataPacket):
    def __init__(self, message:str):
        super().__init__(message)

class ClientBoundPlayerListPacket(ClientBoundDataListPacket):
    def __init__(self, datas:list):
        super().__init__(datas)
    
def getClientBoundPacket(id:int,data:str = "") -> ClientBoundPacket:
    print("client : clientboundget :",data)
    id = data[0]
    packet = clientBoundPacketList[id]
    if issubclass(packet,ClientBoundDataPacket):
       return packet(data)
    else :
        return packet()

clientBoundPacketList = [
    ClientBoundMessagePacket,
    ClientBoundPlayerListPacket,
]
