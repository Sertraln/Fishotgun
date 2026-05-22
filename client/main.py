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
import client.network as network
import client.data as data
from ursina import application as appli
import client.world as world
from client import menu
from client.spot import FishingSpot
from fish import FishingScene
from transitions import IrisTransition,_exit_black
import client.save as save


def custom_quit():
    print("quit")
    if data.network:
        print("Disconnecting from server...")
        data.network.disconnect()
    save.save_global_data()

app = Ursina()
appli.quit = custom_quit
data.init()
menu.init()
world.init_assets()
save.load_global_data()
appli.pause()
window.color = color.gray
_sun_light = DirectionalLight(shadows=True)
_sun_light.look_at(Vec3(0.1,-1,0))
_sun_light._light.specular_color = color.gold
_ambient_light = AmbientLight(color=color.rgba(0.3, 0.28, 0.25, 0.5))

def enter_fishing():
    data.iris.play(on_black=_enter_black)

def _enter_black():
    data.player.disable()
    mouse.locked = False
    data.fishing_scene.start()

def on_fishing_end(result):
    data.iris.play(on_black=_exit_black)

# Fonction update GLOBALE - en dehors de start()


def update():
    player = data.player
    if player is None: return
    # Récupérer les références depuis data
    world.update()
    player = data.player
    spot = next((e for e in data.world_entities if isinstance(e, FishingSpot)), None)
    if spot is None:
        return
    instructions = data.instructions
    iris, fishing_scene = data.iris, data.fishing_scene
    iris.update()

    if fishing_scene.enabled:
        fishing_scene.update()
        return
    
    # Gotta check this for all spots in the map constantly (will need a list later)
    if distance(spot.position, player.position) < spot.interaction_range:
        if held_keys['e']:
            enter_fishing()
        else:
            spot.color = color.yellow
    else:
        spot.color = color.white
    
    # Check if the camera is clipping anywhere
    direction = camera.forward * -1
    offset_clipping = 0.05
    hit_camera = raycast(player.camera_pivot.world_position, direction, -player.camera_offset+offset_clipping, ignore=[player, camera, spot])
    
    if hit_camera.hit:
        camera.z_setter(-hit_camera.distance+offset_clipping)
    else:
        camera.z_setter(player.camera_offset)

    
class MenuLogic(Entity):
    def __init__(self):
        super().__init__(ignore_paused=True)
    def input(self,key):

        if key == 'p' and data.player:
            p = data.player.position
            # print(f"{p.x:.2f},{p.y:.2f},{p.z:.2f}")
            print(f"{p.x:.2f},{p.z:.2f}")
            with open('trees_coord.csv', 'a') as f:
                # f.write(f"{p.x:.2f},{p.y:.2f},{p.z:.2f}\n")
                f.write(f"{p.x:.2f},{p.z:.2f}\n")

        if key == 'escape' and not menu._background_menu.enabled:
            if menu.ispausing() :
                mouse.locked = True
                menu.hide()
            else:
                mouse.locked = False
                menu.show("menu1")
        chat_menu = menu.getMenu("chat")
        if key == 't up' and chat_menu and not chat_menu.enabled:
                menu.show(chat_menu)

MenuLogic()
try: app.run()
except SystemExit: custom_quit()