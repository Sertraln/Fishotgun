import os
import sys
# Ensure project root is on sys.path so sibling packages like `shared` can be imported
_ROOT = os.path.dirname(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from ursina import *
from client.spot import FishingSpot
import client.network as network
import client.data as data
from ursina import application as appli
from shared.world import init_world
from client.world import World
from client import menu
from client.spot import FishingSpot

def custom_quit():
    if data.network:
        print("Disconnecting from server...")
        data.network.disconnect()
    sys.exit()
app = Ursina()
appli.quit = custom_quit

menu.init()
appli.pause()
window.color = color.blue
data.world = World()
original_quit = appli.quit

# Fonction update GLOBALE - en dehors de start()
def update():
    player = data.player
    if player is None: return
    # Récupérer les références depuis data
    player = data.player
    spot : FishingSpot = data.world_entities[1] # Assuming the spot is the second entity in the list
    instructions = data.instructions
    
    # # Make player respawn if he falls
    # if player.y < -10:
    #     player.position = (0, 7, 0)
    #     player.vitesse = Vec3(0,0,0)
    
    # Gotta check this for all spots in the map constantly (will need a list later)
    if distance(spot.position, player.position) < spot.interaction_range:
        if held_keys['e']:
            spot.interact()
        else: 
            spot.color = color.white
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
        if key == 'escape':
            if menu._currentMenu is not None and menu._currentMenu.enabled:
                mouse.locked = True
                menu.hide()
            else:
                mouse.locked = False
                menu.show("menu1")
        chat_menu = menu.getMenu("chat")
        if key == 't up' and chat_menu and not chat_menu.enabled:
                menu.show(chat_menu)

MenuLogic()

app.run()