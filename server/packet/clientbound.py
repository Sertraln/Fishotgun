import socket
from server.packet.packetstruct import ClientBoundDataPacket,ClientBoundPacket

#ClientBound server -> client
#ServerBound client -> server

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
    
