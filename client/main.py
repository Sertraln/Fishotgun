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
from shared.world import init_world, world_scene
from client.world import World

def start(ip:str, port:int, name:str):
    data.world = World()
    data.network = network.Network(ip, port, name)
    original_quit = appli.quit
    
    def custom_quit():
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
    from client.packet.clientbound import ClientBoundInitPlayerPacket
    ClientBoundInitPlayerPacket.init()
    if(not data.world.player_init.wait(5)):  # Wait for player initialization before starting the game loop
        print("Player initialization timed out. Exiting.")
        data.network.disconnect()
        exit(0)
    
    app.run()

# Fonction update GLOBALE - en dehors de start()
def update():
    world_scene.bullet_world.doPhysics(time.dt)


    # Récupérer les références depuis data
    player = data.player
    spot = data.spot
    instructions = data.instructions
            # L'enregistrement dans le world se fait via World.__init__ qui ajoute player_entity


    if not player:
        return

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
    
    # Afficher la position du joueur
    instructions.text = f'''Contrôles:
Z/Q/S/D - Déplacement
Espace - Sauter
Souris - Regarder
Échap - Déverrouiller souris
Position: ({player.position.x:.1f}, {player.position.y:.1f}, {player.position.z:.1f})
Au sol: {'Oui' if data.player.grounded else 'Non'}
'''

if __name__ == '__main__':
    ip = input("Enter server IP (default 127.0.0.1): ")
    port = input("Enter server port (default 5555): ")
    name = input("Enter your player name: ")
    
    if ip == "":
        ip = "127.0.0.1"
    if port == "":
        port = "5555"
    if name == "":
        name = "default"
    
    start(ip, int(port), name)