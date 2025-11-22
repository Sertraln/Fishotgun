import socket
import shared.utils as utils
from server.packet import packetlist as pl

packet_id_map = {}

class ClientBoundPacket:
    def get_id(self):
        if packet_id_map.get(self.__class__) is None:
            packet_id_map[self.__class__] = pl.clientBoundPacketList.index(self.__class__)
        return packet_id_map[self.__class__]
    
    def send(self,conn:socket.socket):
        conn.send(bytes([pl.clientBoundPacketList.index(self.__class__)]))

class ClientBoundDataPacket(ClientBoundPacket):
    def __init__(self,*data:str,datas:list[str] = None ):
        if datas is not None:
            self.data = datas
        else:
            self.data = data

    def send(self, conn):
        packet = utils.parser(self.get_id(),self.data)
        conn.send(packet)

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