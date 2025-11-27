import socket
import shared.packetlib as packetlib
from server.packet import packetlist as pl
from shared.parser import Parser,Wrapper
from abc import abstractmethod

packet_id_map = {}

#===== CLIENT BOUND PACKETS =====#
class ClientBoundPacket:
    def get_id(self):
        if packet_id_map.get(self.__class__) is None:
            packet_id_map[self.__class__] = pl.clientBoundPacketList.index(self.__class__)
        return packet_id_map[self.__class__]
    
    def send(self,conn:socket.socket):
        conn.send(bytes([pl.clientBoundPacketList.index(self.__class__)]))

class ClientBoundDataPacket(ClientBoundPacket):
    def __init__(self,*data:str,func = None,datas:list = None):
        self.data = datas if datas else data
        self.data = func(self.data) if func else self.data

    def send(self, conn):
        packet = packetlib.parser(self.data,self.get_id())
        conn.send(packet)

class ClientBoundDataListPacket(ClientBoundDataPacket):
    def __init__(self,datas:list[str | Parser | Wrapper],func = None):
        if func:
            datas = list(map(func,datas))
        super().__init__(datas=datas)

#===== SERVER BOUND PACKETS =====#
class ServerBoundPacket:
    def get_id(self):
        if packet_id_map.get(self.__class__) is None:
            packet_id_map[self.__class__] = pl.serverBoundPacketList.index(self.__class__)
        return packet_id_map[self.__class__]
    
    def handle(self,client):
        pass

class ServerBoundDataPacket(ServerBoundPacket):
    def __init__(self,data:list[str]):
        self.data = data

