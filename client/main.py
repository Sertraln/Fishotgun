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

def start(ip:str, port:int, name:str):
    data.world = World()
    data.network = network.Network(ip, port, name)
    original_quit = appli.quit
    
    def custom_quit():
        if data.network:
            print("Disconnecting from server...")
            data.network.disconnect()
        original_quit()
    
    app = Ursina()
    data.app = app
    appli.quit = custom_quit
    window.size = (800, 600)
    
    init_world(scene)
    
    instructions = Text(
        text='Contrôles:\nZ/Q/S/D - Déplacement\nEspace - Sauter\nSouris - Regarder\nÉchap - Déverrouiller souris',
        position=(-0.5, 0.4),
        scale=1.2,
        origin=(0, 0),
        background=True
    )

    
    # Create a fishing spot
    spot = FishingSpot(position=(0, 2, 0))
    
    # Set basic sky
    Sky(texture='sky_default')
    light = DirectionalLight(shadows=False)
    light.look_at(Vec3(0.1,-1,0))
    light._light.specular_color = color.gold
    camera.fov = 90
    # Stocker les références dans data pour y accéder dans update
    data.spot = spot
    data.instructions = instructions
    if(not data.world.player_init.wait(5)):  # Wait for player initialization before starting the game loop
        print("Player initialization timed out. Exiting.")
        data.network.disconnect()
        exit(0)
    from client.packet.clientbound import ClientBoundInitPlayerPacket
    ClientBoundInitPlayerPacket.init()
    app.run()

# Fonction update GLOBALE - en dehors de start()
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
    # Récupérer les références depuis data
    player = data.player
    spot = data.spot
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