import socket
import shared.utils as utils
from client.packet import packetlist as pl

packet_id_map = {}

class ClientBoundPacket:
    def get_id(self):
        if packet_id_map.get(self.__class__) is None:
            packet_id_map[self.__class__] = pl.clientBoundPacketList.index(self.__class__)
        return packet_id_map[self.__class__]
    
    def handle(self):
        pass

class ClientBoundDataPacket(ClientBoundPacket):
    def __init__(self,data:list[str]):
        self.data = data

    def __str__(self):
        return "data: "+str(self.data)
    
class ServerBoundPacket:
    def get_id(self):
        if packet_id_map.get(self.__class__) is None:
            packet_id_map[self.__class__] = pl.serverBoundPacketList.index(self.__class__)
        return packet_id_map[self.__class__]

    def send(self,conn:socket.socket):
        conn.send(bytes([pl.serverBoundPacketList.index(self.__class__)]))

class ServerBoundDataPacket(ServerBoundPacket):
    def __init__(self,*data):
        self.data = data

    def send(self, conn):
        print("packetlist:",pl.serverBoundPacketList)
        packet = utils.parser(self.get_id(),self.data)
        conn.send(packet)