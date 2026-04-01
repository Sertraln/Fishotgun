from client import data,menu,network
from client.menus.chat import Chat
from client.spot import FishingSpot
from ursina import Shader,Button,destroy,color,Sky,mouse,Vec3,Text,DirectionalLight,AmbientLight,camera,scene,application
from client.player import Player,ThirdPersonController
import threading
import shared.world as world
from client.transitions import IrisTransition,_exit_black
from client.fish import FishingScene
import time

_sky_entity = None
_water_time_start = None


class World:

    def __init__(self):
        self.players: dict[int,Player] = {}
        self.player_init = threading.Event()
        self.enabled = False

    def spawn_player(self,player_id:int,name:str,position:Vec3,rotation:float=0):
        print(f"World: spawning player {player_id} at {position}")
        new_player = Player(player_id,name=name,position=position)
        new_player.rotation_y = rotation
        self.players[player_id] = new_player

    def leave_player(self,player_id:int):
        print("client : player leave get :",player_id, flush=True)
        if player_id in self.players:
            pl = self.players[player_id]
            destroy(pl)
            del self.players[player_id]
    
    def clear_world(self):
        for pl in self.players.values():
            destroy(pl)
        self.players.clear()
        self.enabled = False

class PlayerInitializationError(Exception):
    pass

def join_world(ip:str, port:int, name:str) -> Exception | None:
    try:
        from client.packet.clientbound import ClientBoundInitPlayerPacket
        ClientBoundInitPlayerPacket.player = None
        data.world.player_init.clear()
        data.network = network.Network(ip,port,name)
        if(not data.world.player_init.wait(5)):  # Wait for player initialization before starting the game loop
            print("Player initialization timed out. Exiting.")
            data.network.disconnect()
            raise PlayerInitializationError("Player initialization timed out.")
        ClientBoundInitPlayerPacket.init()
    except Exception as e:
        data.network = None
        data.world.clear_world()
        raise e
    load_world()
    return None

def init_assets():
    #TODO: only load at the start of the game, not every time we join a world
    pass

def load_world():
    global _sky_entity, _water_time_start
    water_shader_path = application.asset_folder / 'assets' / 'shader' / 'water.fsh'
    water_shader_fragment = water_shader_path.read_text(encoding='utf-8')

    _sky_entity = Sky(color=color.violet)
    world.init_world(scene)

    if world.ground is None or world.water is None:
        raise RuntimeError("world.init_world() n'a pas initialisé ground/water")
    data.instructions = Text(
        text='Contrôles:\nZ/Q/S/D - Déplacement\nEspace - Sauter\nSouris - Regarder\nÉchap - Déverrouiller souris',
        position=(-0.5, 0.4),
        scale=1.2,
        origin=(0, 0),
        background=True
    )
    spot = FishingSpot(position=(0,2,0))
    data.world_entities = [spot]
    camera.fov = 90


    data.iris = IrisTransition(close_duration=0.8, black_duration=0.5, open_duration=0.8)

    
    def on_fishing_end(result):
        data.iris.play(on_black=_exit_black)

    data.fishing_scene = FishingScene(on_end=on_fishing_end)

    
    spot.set_scene(data.fishing_scene)

    #loading textures
    world.ground.texture = 'assets/textures/grass.png'
    world.ground.texture_scale = (64,64)
    world.water.texture = 'assets/textures/water.png'
    world.water.texture_scale = (64,64)
    water_shader = Shader(name="water", vertex=data.default_vertex, fragment=water_shader_fragment)
    water_shader.compile()
    world.water.model.setShader(water_shader._shader)
    _water_time_start = time.perf_counter()
    world.water.model.set_shader_input("iTime", 0.0)
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
    from client.packet.clientbound import ClientBoundInitPlayerPacket

    menu.show("main_menu")

    global _sky_entity, _water_time_start
    if _sky_entity:
        destroy(_sky_entity)
        _sky_entity = None
    _water_time_start = None

    if data.network is not None:
        # Avoid recursive quit_to_menu calls from Network.disconnect().
        data.network.disconnect(trigger_quit_to_menu=False)

    if data.player:
        try:
            data.player.disable()
        except Exception:
            pass
        destroy(data.player)
        data.player = None

    if data.world is not None:
        for p in list(data.world.players.values()):
            p.disable()
            destroy(p)
        data.world.players.clear()

    # Prevent stale references across sessions.
    ClientBoundInitPlayerPacket.player = None

    if world.ground:
        destroy(world.ground)
        world.ground = None
    
    if world.water:
        destroy(world.water)
        world.water = None

    for e in data.world_entities:
        destroy(e)
    data.world_entities = []

    if 'menu1' in menu._menus:
        destroy(menu._menus['menu1'])
        del menu._menus['menu1']

def update():
    if not world.water or not world.water.model:
        return

    # Relative monotonic time keeps animation smooth on GLSL 120 by avoiding huge epoch values.
    if _water_time_start is None:
        t = 0.0
    else:
        t = time.perf_counter() - _water_time_start

    world.water.model.set_shader_input("iTime", t % 4096.0)

# Initialize the world instance after defining the World class
data.world = World()