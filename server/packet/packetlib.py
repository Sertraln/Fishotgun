import os
import sys

if __name__ == "__main__":
    # Ensure project root is on sys.path so sibling packages like `shared` can be imported
    _ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from shared import packetlib
from shared.loadfile import get_defined_classes
from server.packet.packetstruct import *
from server.packet import packetlist as pl

def init_packetlib():
    pl.clientBoundPacketList = get_defined_classes("server/packet/clientbound.py")
    pl.serverBoundPacketList = get_defined_classes("server/packet/serverbound.py")
    packetlib.clientBoundDataPacket = [issubclass(packet,ClientBoundDataPacket) for packet in pl.clientBoundPacketList]
    packetlib.serverBoundDataPacket = [issubclass(packet,ServerBoundDataPacket) for packet in pl.serverBoundPacketList]
    packetlib.init()

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
    list = packetlib.unparse(data,False)
    for id,decode in list:
        packet = pl.serverBoundPacketList[id]
        if issubclass(packet,ServerBoundDataPacket):
            result.append(packet(decode))
        else :
            result.append(packet())
    return result

if __name__ == "__main__":
    init_packetlib()
    print("Client Bound Packets:", pl.clientBoundPacketList)
    print("Server Bound Packets:", pl.serverBoundPacketList)
    a = packetlib.unparse(b'\x01\x01\x0f\x05\x02\x02\t\x00\x00\x03\x18\x87\xe9\xb9\xdb\xe2\x83D',False)
    print(a)