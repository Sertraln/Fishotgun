from client.packet.packetstruct import ClientBoundPacket,ClientBoundDataPacket
from ursina import Vec3
import client.data as data
#client_bound server -> client
#server_bound client -> server

#exist only for the parity in numbering packet id, not used in code
class ClientBoundIdPacket(ClientBoundPacket):
    pass

class ClientBoundInitPlayerPacket(ClientBoundDataPacket):
    player = None

    def __init__(self,data:list):
        super().__init__(data)
        self.position = self.data[0]
        self.fishunlocked = self.data[1]
         # Reset player reference on new init packet

    def handle(self):
        if data.player is None:
            data.world.player_init.set()  # Signal that the player has been initialized
            ClientBoundInitPlayerPacket.player = self
        else:
            print("client : init player packet received but player already exist", flush=True)

    def init():
        if ClientBoundInitPlayerPacket.player is None:
            print("client : waiting for init player packet...", flush=True)
            return
        from client.player import ThirdPersonController
        data.player = ThirdPersonController(data.network.id,data.network.name, position=ClientBoundInitPlayerPacket.player.position)

class ClientBoundMessagePacket(ClientBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)
        self.message = self.data[0]

    def handle(self):
        #TODO l.chat.addMessage(self.message)
        pass

class ClientBoundPlayerListPacket(ClientBoundDataPacket):
    def __init__(self,data:list[list[int | str | Vec3]]):
        super().__init__(data)

    def handle(self):
        print("client : player list get :",self.data, flush=True)
        for player_data in self.data:
            player_id : int = player_data[0]
            name : str = player_data[1]
            position : Vec3 = player_data[2]
            rotation : float = player_data[3]
            data.world.spawn_player(player_id,name,position,rotation)

class ClientBoundSpawnPlayerPacket(ClientBoundDataPacket):
    def __init__(self,data:list[int | str | Vec3]):
        super().__init__(data)
        self.player_id : int = data[0]
        self.name : str = data[1]
        self.position : Vec3 = data[2]
        self.rotation : float = data[3]

    def handle(self):
        data.world.spawn_player(self.player_id,self.name,self.position,self.rotation)

class ClientBoundPlayerLeavePacket(ClientBoundDataPacket):
    def __init__(self,data:list[int]):
        super().__init__(data)
        self.player_id : int = data[0]

    def handle(self):
        data.world.leave_player(self.player_id)

class ClientBoundPlayerPositionPacket(ClientBoundDataPacket):
    def __init__(self,data:list):
        super().__init__(data)
        self.player_id : int = data[0]
        self.position : Vec3 = data[1]

    def handle(self):
        print("client : player position get :",self.player_id,self.position, flush=True)
        data.world.players[self.player_id].set_target_position(self.position)

class ClientBoundReconcilePositionPacket(ClientBoundDataPacket):
    def __init__(self,data:list):
        super().__init__(data)
        self.timestamp : int = data[0]
        self.position : Vec3 = data[1]

    def handle(self):
        print("client : player reconcile position get :",self.timestamp,self.position, flush=True)
        data.player.register_server_pos(self.timestamp,self.position)

class ClientBoundPlayerRotationPacket(ClientBoundDataPacket):
    def __init__(self,data:list):
        super().__init__(data)
        self.player_id : int = data[0]
        self.rotation : float = data[1]

    def handle(self):
        print("client : player rotation get :",self.player_id,self.rotation, flush=True)
        if self.player_id == data.player.player_id:
            return  # Ignore rotation updates for the local
        data.world.players[self.player_id].set_target_rotation(self.rotation)