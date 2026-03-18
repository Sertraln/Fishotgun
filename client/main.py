import os
import sys

# Ensure project root is on sys.path so sibling packages like `shared` can be imported
_ROOT = os.path.dirname(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from ursina import *
import data
from ursina import application as appli
from client import menu

Plane
original_quit = appli.quit
def custom_quit():
    if data.network:
        print("Disconnecting from server...")
        data.network.disconnect()
    original_quit()
app = Ursina()
appli.quit = custom_quit

menu.init()
appli.pause()
window.color = color._20


def update():
    player = data.player
    if player is None: return

    # Make player respawn if he falls
    if player.y < -10:
        player.position = (0,4,0)
    
    # Kick player if flies example
    if player.air_time > 10:
        pass

    # Kick player if too fast
    if player.speed > 21:
        pass
    
    # Sprints if shift is held
    if held_keys['shift']:
        player.body.color = color.red
        player.speed = 20
    else:
        player.body.color = color.blue
        player.speed = 10
    
    # Gotta check this for all spots in the map constantly (will need a list later)
    # if distance(spot.position, player.position) < spot.interaction_range:
    #     pass

    # Check if the camera is clipping anywhere
    direction = camera.forward * -1
    offset_clipping = 0.05
    hit_camera = raycast(player.camera_pivot.world_position,direction,-player.camera_offset+offset_clipping,ignore=[player,player.body,camera,spot])
    if hit_camera.hit :
        print(hit_camera.distance,hit_camera.point)
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