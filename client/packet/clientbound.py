from client.packet.packetstruct import ClientBoundPacket,ClientBoundDataPacket
#client_bound server -> client
#server_bound client -> server

class ClientBoundIdPacket(ClientBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)
        self.id = int(data[0])

    def handle(self):
        pass

class ClientBoundMessagePacket(ClientBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)
        self.message = self.data[0]

    def handle(self):
        #TODO l.chat.addMessage(self.message)
        pass

class ClientBoundPlayerListPacket(ClientBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)

    def handle(self):
        pass


    

