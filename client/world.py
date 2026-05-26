from client import data,menu,network
import os, csv
from client.menus.chat import Chat
from client.spot import FishingSpot
from ursina import Shader,Button,destroy,color,Sky,mouse,Vec3,Text,camera,scene,application,Entity
from client.player import Player
import threading
import shared.world as world
from client.transitions import IrisTransition,_exit_black
from client.fish import FishingScene
import time
from panda3d.core import PandaNode, NodePath
from direct.actor.Actor import Actor
import copy

_sky_entity = None
_water_time_start = None
class WorldScene(Entity):
    def __init__(self):
        super().__init__()
        self.name="world_base"
        self.ui = Entity(parent=camera.ui)
        self.disable()

    def disable(self):
        print("Disabling world scene")
        super().disable()
        self.ui.disable()
        menu.show_background()
        data.hud.disable()

    def enable(self):
        print("Enabling world scene")
        super().enable()
        self.ui.enable()
        menu._background_menu.hide()
        data.hud.enable()

_world =None
    
shopkeeper = None

class World:
    def __init__(self):
        self.players: dict[int,Player] = {}
        self.player_init = threading.Event()
        self.enabled = False

    def spawn_player(self,player_id:int,name:str,position:Vec3,rotation:float=0):
        print(f"World: spawning player {player_id} at {position}")
        new_player = Player(player_id,name=name,position=position)
        data.player = new_player
        new_player.rotation_y = rotation
        self.players[player_id] = new_player

    def leave_player(self,player_id:int):
        print("client : player leave get :",player_id, flush=True)
        if player_id in self.players:
            pl = self.players[player_id]
            pl.detach_node()
            del self.players[player_id]
    
    def clear_world(self):
        for pl in self.players.values():
            destroy(pl)
        self.players.clear()

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

def spawn_spots(l):
    _ROOT = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(_ROOT, 'shared', 'data', 'pdpeche.csv')
    scale_factor = 3
    
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier est introuvable à : {file_path}")
        return

    with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                l.append(FishingSpot(
                    position=(-float(row['x'])*scale_factor, 2, -float(row['y'])*scale_factor),
                    color = color.rgba(0, 0, 0, 0),
                    parent=scene
                ))

def init_assets():
    global _sky_entity, _water_time_start,_world
    _world = WorldScene()
    water_shader_path = application.asset_folder / 'assets' / 'shader' / 'water.fsh'
    water_shader_fragment = water_shader_path.read_text(encoding='utf-8')
    _sky_entity = Sky(color=color.violet,parent=_world)
    world.init_world(_world)

    if world.ground is None or world.water is None:
        raise RuntimeError("world.init_world() n'a pas initialisé ground/water")
    data.world_entities = []
    spawn_spots(data.world_entities)
    camera.fov = 90

    data.iris = IrisTransition(close_duration=0.8, black_duration=0.5, open_duration=0.8)

    def on_fishing_end(result):
        data.iris.play(on_black=_exit_black)

    data.fishing_scene = FishingScene(on_end=on_fishing_end)
    #loading textures
    world.ground.texture = 'assets/textures/grass.png'
    world.ground.texture_scale = (64,64)

    world.water.texture = 'assets/textures/water.png'
    world.water.texture_scale = (64,64)
    water_shader = Shader(name="water", vertex=data.default_vertex, fragment=water_shader_fragment)
    water_shader.compile()
    world.water.model.set_shader_input("texScale", 128.0)
    world.water.model.setShader(water_shader._shader)
    _water_time_start = time.perf_counter()
    world.water.model.set_shader_input("iTime", 0.0)

    #registering menus
    menu1 = menu.Menu("menu1", True, True)
    node = copy.deepcopy(menu._background_menu.paper)
    node.parent = menu1
    node.position = (0,0,1)
    resume = menu.FixedButton(text='Resume', scale=(0.3, 0.1), position=(0,0.1),text_size=2)
    def resume_game():
        menu.hide()
        mouse.locked = True
    resume.on_click = resume_game
    menu1.add_element(resume)
    quit = menu.FixedButton(text='Quit', scale=(0.3, 0.1), position=(0,-0.1),text_size=2)
    quit.on_click = quit_to_menu
    menu1.add_element(quit)
    ChatMenu = Chat()
    menu.register_menu(ChatMenu)
    menu.register_menu(menu1)
    global shopkeeper
    shopkeeper = Actor('assets/models/Shopkeeper.glb')
    shopkeeper.reparent_to(_world)
    shopkeeper.set_pos(world.get_shopkeeper_pos())
    shopkeeper.set_hpr(90, 360, 0)
    shopkeeper.set_scale(1.2)
    shopkeeper.name = 'shopkeeper'
    shopkeeper.loop('idle')
    

def load_world():
    _world.enable()

def quit_to_menu():
    def on_black():
        from ursina import destroy
        from client.packet.clientbound import ClientBoundInitPlayerPacket

        menu.show("main_menu")
        menu.show_background()
        _world.disable()

        if data.network is not None:
            data.network.disconnect(trigger_quit_to_menu=False)
            data.network = None

        if data.player:
            try:
                data.player.disable()
            except Exception:
                pass
            destroy(data.player)
            data.player = None

        if data.world is not None:
            data.world.players.clear()

        data.world_entities.clear()
        ClientBoundInitPlayerPacket.player = None

    # Lance la transition en passant la fonction on_black comme callback
    data.iris.play(on_black=on_black)

def update():
    if not world.water or not world.water.model:
        return

    if _water_time_start is None:
        t = 0.0
    else:
        t = time.perf_counter() - _water_time_start

    world.water.model.set_shader_input("iTime", t % 4096.0)

data.world = World()