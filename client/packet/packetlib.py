import os
import sys

if __name__ == "__main__":
    # Ensure project root is on sys.path so sibling packages like `shared` can be imported
    _ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from shared import packetlib
from shared.loadfile import get_defined_classes
from client.packet.packetstruct import *
from client.packet import packetlist

def init_packetlib():
    packetlist.clientBoundPacketList = get_defined_classes("client/packet/clientbound.py")
    packetlist.serverBoundPacketList = get_defined_classes("client/packet/serverbound.py")
    packetlib.clientBoundDataPacket = [issubclass(packet,ClientBoundDataPacket) for packet in packetlist.clientBoundPacketList]
    packetlib.serverBoundDataPacket = [issubclass(packet,ServerBoundDataPacket) for packet in packetlist.serverBoundPacketList]
    packetlib.init()

def getClientBoundPacket(data:bytes) -> list[ClientBoundPacket]:
    print("client : clientboundget :",data)
    result = []
    list = packetlib.unparse(data,True)
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
    from shared.parsedata.input import KeyStates
    a = packetlib.parser(1,(KeyStates.FORWARD,123456789))
    b = packetlib.unparse(b'\x03\x01\x13\x04\x02\x02\r\x03\x00\x01\x00\x00\x00\x00\xc4\x9c\xef\xa0?\xb7\xaaC',True)
    print(b)