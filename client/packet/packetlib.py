from shared import utils

class ClientBoundPacket:
    def get_id(self):
        return clientBoundPacketList.index(self.__class__)
    
    def handle(self):
        pass

class ClientBoundDataPacket(ClientBoundPacket):
    def __init__(self,data:list[str]):
        self.data = data

def getClientBoundPacket(data:bytes) -> list[ClientBoundPacket]:
    print("client : clientboundget :",data)
    result = []
    list = utils.unparse(data,True)
    for id,decode in list:
        packet = clientBoundPacketList[id]
        if issubclass(packet,ClientBoundDataPacket):
            result.append(packet(decode))
        else :
            result.append(packet())
    return result

clientBoundPacketList = getFromFile

utils.clientBoundDataPacket = [issubclass(packet,ClientBoundDataPacket) for packet in clientBoundPacketList]