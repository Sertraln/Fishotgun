from client import data,menu,network
from client.menus.chat import Chat
from client.spot import FishingSpot
from ursina import application,Button,Entity,color,Sky,mouse,Vec3,Text,DirectionalLight,AmbientLight,camera,scene
from client.player import Player,ThirdPersonController
import threading
import shared.world as world

class World:

    def __init__(self):
        self.players: dict[int,Player] = {}
        self.player_init = threading.Event()
        world.ground.texture = 'assets/textures/grass.png'
        world.ground.texture_scale = (128,128)
        world.water.texture = 'assets/textures/water.png'
        world.water.texture_scale = (64,64)


    def spawn_player(self,player_id:int,name:str,position:Vec3,rotation:float=0):
        print(f"World: spawning player {player_id} at {position}")
        new_player = Player(player_id,name=name,position=position)
        new_player.rotation_y = rotation
        self.players[player_id] = new_player

    def leave_player(self,player_id:int):
        print("client : player leave get :",player_id, flush=True)
        if player_id in self.players:
            del self.players[player_id]

class PlayerInitializationError(Exception):
    pass

def join_world(ip:str, port:int, name:str) -> Exception | None:
    try:
        data.network = network.Network(ip,port,name)
        if(not data.world.player_init.wait(5)):  # Wait for player initialization before starting the game loop
            print("Player initialization timed out. Exiting.")
            data.network.disconnect()
            return PlayerInitializationError("Player initialization timed out.")
        from client.packet.clientbound import ClientBoundInitPlayerPacket
        ClientBoundInitPlayerPacket.init()
    except Exception as e:
        return e
    load_world()
    return None

def load_world():
    sky = Sky(color=color.violet)
    world.init_world(scene)
    data.instructions = Text(
        text='Contrôles:\nZ/Q/S/D - Déplacement\nEspace - Sauter\nSouris - Regarder\nÉchap - Déverrouiller souris',
        position=(-0.5, 0.4),
        scale=1.2,
        origin=(0, 0),
        background=True
    )
    data.world = World()
    spot = FishingSpot(position=(0,2,0))
    data.world_entities = [sky, spot]
    light = DirectionalLight(shadows=False)
    light.look_at(Vec3(0.1,-1,0))
    light._light.specular_color = color.gold
    ambient = AmbientLight(color=color.rgba(0.2, 0.2, 0.2, 0.5))
    data.world_entities.extend([light, ambient])
    camera.fov = 90
    #registering menus
    menu1 = menu.Menu("menu1", False)
    resume = Button(text='Resume', scale=(0.3, 0.1), position=(0,0.1))
    def resume_game():
        menu.hide()
        mouse.locked = True
    resume.on_click = resume_game
    menu1.add_element(resume)
    quit = Button(text='Quit', scale=(0.3, 0.1), position=(0,-0.1))
    quit.on_click = quit_to_menu
    menu1.add_element(quit)
    ChatMenu = Chat()
    menu.register_menu(ChatMenu)
    menu.register_menu(menu1)

def quit_to_menu():
    from ursina import destroy
    from client.player import player_map

    menu.show("main_menu")

    if data.network:
        data.network.disconnect()
        data.network = None

    if data.player:
        data.player.disable()
        destroy(data.player)
        data.player = None

    for p in list(player_map.values()):
        p.disable()
        destroy(p)
    player_map.clear()

    for e in data.world_entities:
        destroy(e)
    data.world_entities = []

    if 'menu1' in menu._menus:
        destroy(menu._menus['menu1'])
        del menu._menus['menu1']

    data.world = None