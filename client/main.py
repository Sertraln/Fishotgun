import os
import sys
# Ensure project root is on sys.path so sibling packages like `shared` can be imported
_ROOT = os.path.dirname(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import ursina.shader as shader

test_vertex = '''
#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;

varying vec2 uv;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uv = p3d_MultiTexCoord0;
}'''

shader.default_vertex_shader = test_vertex
from ursina import *
import client.data as data
from ursina import application as appli
import client.world as world
from client import menu
from client.spot import FishingSpot
from client.transitions import _exit_black
import client.save as save
import menus
from client.shop import open_shop_dialogue

from client.packet.serverbound import ServerBoundRequestFishingPacket

def custom_quit():
    print("quit")
    if data.network:
        net = data.network
        data.network = None 
        try:
            net.disconnect()
        except:
            pass
    try:
        save.save_global_data()
    except:
        pass

app = Ursina()#development_mode=False)
appli.quit = custom_quit
import client.menus.fishodex as fishodex
data.init()
menu.init()
world.init_assets()
save.load_global_data()
from client.menus.mainmenu import join_menu
if len(join_menu.button_list.children) == 0:
    join_menu.add_server_to_list("localhost", "0.0.0.0", 5555)
appli.pause()
window.color = color.gray
_sun_light = DirectionalLight(shadows=True)
_sun_light.look_at(Vec3(0.1,-1,0))
_sun_light._light.specular_color = color.gold
_ambient_light = AmbientLight(color=color.rgba(0.31, 0.28, 0.25, 0.5))

def enter_fishing():
    data.iris.play(on_black=_enter_black)

def _enter_black():
    data.player.disable()
    mouse.locked = False
    if data.network:
        data.network.send(ServerBoundRequestFishingPacket())

def on_fishing_end(result):
    data.iris.play(on_black=_exit_black)

interact_text = Text(text="Appuyez sur 'E' pour interagir", parent=menus.hud, enabled=False, position=(0, -0.45), origin=(0,0), scale=2, font = data.fisho_font)
shop_done = False
fish_done = False

def update():
    world.update()

    if hasattr(data, 'iris') and data.iris._state != data.iris.IDLE:
        data.iris.update()
        return

    player = data.player
    if not player or getattr(player, 'destroyed', False):
        return
        
    spot = next((e for e in data.world_entities if not getattr(e, 'destroyed', False) and isinstance(e, FishingSpot)), None)

    if not spot:
        return

    if data.fishing_scene.enabled:
        data.fishing_scene.update()
        return
    
    global shop_done, fish_done
    show_interact = False

    if world.shopkeeper and not getattr(world.shopkeeper, 'destroyed', False):
        if distance(player.position, world.shopkeeper.get_pos()) < 4:
            if held_keys['e'] and not shop_done:
                open_shop_dialogue()
                shop_done = True
            if not shop_done:
                show_interact = True
        else:
            shop_done = False

    fishing_spots = [e for e in data.world_entities if not getattr(e, 'destroyed', False) and isinstance(e, FishingSpot)]

    for spot in fishing_spots:
        if distance(spot.position, player.position) < spot.interaction_range:
            if held_keys['e'] and not fish_done:
                enter_fishing()
                data.hud.hide()
                fish_done = True
            
            if not fish_done:
                show_interact = True

    if not held_keys['e']:
        fish_done = False

    interact_text.enabled = show_interact

    direction = camera.forward * -1
    hit_camera = raycast(player.camera_pivot.world_position, direction, -player.camera_offset + 0.05, ignore=[player, camera, spot])
    
    if hit_camera.hit:
        camera.z_setter(-hit_camera.distance + 0.05)
    else:
        camera.z_setter(player.camera_offset)

    
class MenuLogic(Entity):
    def __init__(self):
        super().__init__(ignore_paused=True)

    def input(self,key):
        if not world._world.enabled:
            return
        if key == 'escape':
            if menu.hasMenuShow():
                mouse.locked = True
                menu.hide()
            else:
                mouse.locked = False
                menu.show("menu1")
        chat_menu = menu.getMenu("chat")
        if key == 't up' and chat_menu and not chat_menu.enabled:
                menu.show(chat_menu)
        fishodex = menu.getMenu("fishodex")
        if key == 'f':
            if fishodex and fishodex.enabled:
                mouse.locked = True
                menu.hide()
            elif not menu.hasMenuShow() and fishodex and not fishodex.enabled:
                mouse.locked = False
                menu.show("fishodex")



MenuLogic()

try: app.run()
except SystemExit: custom_quit()