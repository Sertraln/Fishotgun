from shared import utils
from shared.packetlib import get_defined_classes
from server.packet.packetstruct import *
from server.packet import packetlist

def init_packetlib():
    packetlist.clientBoundPacketList = get_defined_classes("client/packet/clientbound.py")
    packetlist.serverBoundPacketList = get_defined_classes("client/packet/serverbound.py")
    utils.clientBoundDataPacket = [issubclass(packet,ClientBoundDataPacket) for packet in packetlist.clientBoundPacketList]
    utils.serverBoundDataPacket = [issubclass(packet,ServerBoundDataPacket) for packet in packetlist.serverBoundPacketList]

def getClientBoundPacket(id:int,data:str = "") -> ClientBoundPacket:
    print("client : clientboundget :",data)
    id = data[0]
    packet = clientBoundPacketList[id]
    if issubclass(packet,ClientBoundDataPacket):
       return packet(data)
    else :
        return packet()

def getServerBoundPacket(data:bytes) -> list[ServerBoundPacket]:
    print("server : serverboundget :",data)
    result = []
    list = utils.unparse(data,False)
    for id,decode in list:
        packet = serverBoundPacketList[id]
        if issubclass(packet,ServerBoundDataPacket):
            result.append(packet(decode))
        else :
            result.append(packet())
    return result