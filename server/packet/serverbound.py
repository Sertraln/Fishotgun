import shared.utils as utils
import server.packet.clientbound as cb
import threading as th


#client_bound server -> client
#server_bound client -> server

class ServerBoundPacket:
    def get_id(self):
        return serverBoundPacketList.index(self.__class__)
    
    def handle(self,client):
        pass

class ServerBoundDataPacket(ServerBoundPacket):
    def __init__(self,data:list[str]):
        self.data = data
        

class ServerBoundPseudoPacket(ServerBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)
        print(data)
        self.name = data[0]

class ServerBoundMessagePacket(ServerBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)
        self.message = data[0]

    def handle(self, client):
        print("server : message get :",self.message, flush=True)
        client.server.broadcast(cb.ClientBoundMessagePacket(self.message),[client.id])


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
    
serverBoundPacketList = [
    ServerBoundPseudoPacket,
    ServerBoundMessagePacket,
]