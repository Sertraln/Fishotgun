import os
import sys

if __name__ == "__main__":
    # Ensure project root is on sys.path so sibling packages like `shared` can be imported
    _ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from shared import utils
from shared.packetlib import get_defined_classes
from client.packet.packetstruct import *
from client.packet import packetlist

def init_packetlib():
    packetlist.clientBoundPacketList = get_defined_classes("client/packet/clientbound.py")
    packetlist.serverBoundPacketList = get_defined_classes("client/packet/serverbound.py")
    utils.clientBoundDataPacket = [issubclass(packet,ClientBoundDataPacket) for packet in packetlist.clientBoundPacketList]
    utils.serverBoundDataPacket = [issubclass(packet,ServerBoundDataPacket) for packet in packetlist.serverBoundPacketList]

def getClientBoundPacket(data:bytes) -> list[ClientBoundPacket]:
    print("client : clientboundget :",data)
    result = []
    list = utils.unparse(data,True)
    for id,decode in list:
        packet = pl.clientBoundPacketList[id]
        if issubclass(packet,ClientBoundDataPacket):
            result.append(packet(decode))
        else :
            result.append(packet())
    return result

def getServerBoundPacket(id:int,data:str = "") -> ServerBoundPacket:
    print("client : serverboundget :",data)
    id = data[0]
    packet = pl.serverBoundPacketList[id]
    if issubclass(packet,ServerBoundDataPacket):
       return packet(data)
    else :
        return packet()

if __name__ == "__main__":
    init_packetlib()
    print("Client Bound Packets:", packetlist.clientBoundPacketList)
    print("Server Bound Packets:", packetlist.serverBoundPacketList)