from shared import utils
from shared.packetlib import get_defined_classes
from server.packet.packetstruct import *
from server.packet import packetlist as pl

def init_packetlib():
    pl.clientBoundPacketList = get_defined_classes("server/packet/clientbound.py")
    pl.serverBoundPacketList = get_defined_classes("server/packet/serverbound.py")
    utils.clientBoundDataPacket = [issubclass(packet,ClientBoundDataPacket) for packet in pl.clientBoundPacketList]
    utils.serverBoundDataPacket = [issubclass(packet,ServerBoundDataPacket) for packet in pl.serverBoundPacketList]
    utils.init()

def getClientBoundPacket(id:int,data:str = "") -> ClientBoundPacket:
    print("client : clientboundget :",data)
    id = data[0]
    packet = pl.clientBoundPacketList[id]
    if issubclass(packet,ClientBoundDataPacket):
       return packet(data)
    else :
        return packet()

def getServerBoundPacket(data:bytes) -> list[ServerBoundPacket]:
    print("server : serverboundget :",data)
    result = []
    list = utils.unparse(data,False)
    for id,decode in list:
        packet = pl.serverBoundPacketList[id]
        if issubclass(packet,ServerBoundDataPacket):
            result.append(packet(decode))
        else :
            result.append(packet())
    return result