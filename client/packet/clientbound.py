from client.packet.packetstruct import ClientBoundPacket,ClientBoundDataPacket
from ursina import Vec3
import client.menu as menu
import client.data as data
#client_bound server -> client
#server_bound client -> server

#exist only for the parity in numbering packet id, not used in code
class ClientBoundIdPacket(ClientBoundPacket):
    pass

class ClientBoundInitPlayerPacket(ClientBoundDataPacket):
    player = None

    def __init__(self,data:list[object]):
        super().__init__(data)
        self.position = self.data[0]
        self.fishunlocked = self.data[1]
        # Reset player reference on new init packet

    def handle(self):
        if data.player is None:
            data.world.player_init.set()  # Signal that the player has been initialized
            ClientBoundInitPlayerPacket.player = self
            
            # AJOUT ICI : Inspecter les données brutes reçues du serveur
            print("=== DEBUG SERVEUR : Paquet d'initialisation reçu ===")
            print(f"Position : {self.position}")
            if hasattr(self.fishunlocked, 'fish_list'):
                print(f"Bitmask fish_list (int) : {self.fishunlocked.fish_list.value}")
            if hasattr(self.fishunlocked, 'capacity'):
                print(f"Quantités par index : {self.fishunlocked.capacity}")
            print("====================================================")
        else:
            print("client : init player packet received but player already exist", flush=True)

    def init():
        if ClientBoundInitPlayerPacket.player is None:
            print("client : waiting for init player packet...", flush=True)
            return
        from client.player import ThirdPersonController
        data.player = ThirdPersonController(data.network.id,data.network.name,
                                            position=ClientBoundInitPlayerPacket.player.position,
                                            fish_inventory=ClientBoundInitPlayerPacket.player.fishunlocked)

        if hasattr(menu, 'menus') and 'fishodex' in menu.menus:
            f_menu = menu.menus['fishodex']
            f_menu.rightpage.update_display(data.player.fish_inventory)
            f_menu.middlepage.update_display(data.player.fish_inventory)
            f_menu.leftpage.update_display(data.player.fish_inventory)
class ClientBoundMessagePacket(ClientBoundDataPacket):
    def __init__(self,data:list[str]):
        super().__init__(data)
        self.origine = data[0]  
        self.message = self.data[1]

    def handle(self):
        menu.getMenu("chat").add_message(self.origine,self.message)

class ClientBoundPlayerListPacket(ClientBoundDataPacket):
    def __init__(self,data:list[list[int | str | Vec3]]):
        super().__init__(data)

    def handle(self):
        # print("client : player list get :",self.data, flush=True)
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
        print("client : player position get :",data.world.players, flush=True)
        data.world.players[self.player_id].set_target_position(self.position)

class ClientBoundReconcilePositionPacket(ClientBoundDataPacket):
    def __init__(self,data:list):
        super().__init__(data)
        self.timestamp : int = data[0]
        self.position : Vec3 = data[1]

    def handle(self):
        #print("client : player reconcile position get :",self.timestamp,self.position, flush=True)
        data.player.register_server_pos(self.timestamp,self.position)

class ClientBoundAddFishPacket(ClientBoundDataPacket):
    def __init__(self, data: list):
        super().__init__(data)
        self.fish_flag = data[0] 

    def handle(self):
        import client.data as data
        from shared.parsedata.fishlist import FishList
        
        if hasattr(data, 'player') and data.player and hasattr(data.player, 'fish_inventory'):
            inv = data.player.fish_inventory
            inv.fish_list.unlock(self.fish_flag)
            
            index = FishList.ordinal(self.fish_flag)
            if index < len(inv.capacity):
                inv.capacity[index] += 1
                
            print(f"Client : Inventaire synchronisé pour {self.fish_flag.name}")

class ClientBoundClearInventoryPacket(ClientBoundPacket):
    def __init__(self):
        super().__init__()

    def handle(self):
        print("clear inventory")
        data.player.fish_inventory.clear_inventory()

class ClientBoundFishingSessionPacket(ClientBoundDataPacket):
    def __init__(self, data: list):
        super().__init__(data)
        self.fish_ids: list[int] = data[0]

    def handle(self):
        import client.data as data
        if hasattr(data, 'fishing_scene') and data.fishing_scene:
            data.fishing_scene.start(self.fish_ids)