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

def start(ip:str, port:int, name:str):
    data.network = network.Network(ip, port, name)
    original_quit = appli.quit
    
    def custom_quit():
        print("Disconnecting from server...")
        data.network.disconnect()
        original_quit()
    
    app = Ursina()
    data.app = app
    appli.quit = custom_quit
    
    # Create ground
    ground = Entity(
        model='cube',
        scale=(100, 10, 100),
        texture='grass',
        texture_scale=(10, 10),
        collider='box')
    
    instructions = Text(
        text='Contrôles:\nZ/Q/S/D - Déplacement\nEspace - Sauter\nSouris - Regarder\nÉchap - Déverrouiller souris',
        position=(-0.5, 0.4),
        scale=1.2,
        origin=(0, 0),
        background=True
    )
    
    from client.data import player
    from client.player import ThirdPersonController
    player = ThirdPersonController(position=(0, 2, 0))
    # Set cursor white cause pink ugly af
    player.cursor.color = color.white
    
    # Create a fishing spot
    spot = FishingSpot(position=(0, 2, 0))
    
    # Set basic sky
    Sky(color=color.violet)
    
    # Stocker les références dans data pour y accéder dans update
    data.player = player
    data.spot = spot
    data.instructions = instructions
    
    app.run()

# Fonction update GLOBALE - en dehors de start()
def update():
    # Récupérer les références depuis data
    player = data.player
    spot = data.spot
    instructions = data.instructions
    
    # Make player respawn if he falls
    if player.y < -10:
        player.position = (0, 4, 0)
    
    # Kick player if flies example
    if player.air_time > 10:
        pass
    
    # Kick player if too fast
    if player.speed > 21:
        pass
    
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
    hit_camera = raycast(player.camera_pivot.world_position, direction, -player.camera_offset+offset_clipping, ignore=[player, player.body, camera, spot])
    
    if hit_camera.hit:
        print(hit_camera.distance, hit_camera.point)
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
Au sol: {'Oui' if player.grounded else 'Non'}'''

if __name__ == '__main__':
    ip = input("Enter server IP (default 192.168.64.9): ")
    port = input("Enter server port (default 5555): ")
    name = input("Enter your player name: ")
    
    if ip == "":
        ip = "192.168.64.9"
    if port == "":
        port = "5555"
    if name == "":
        name = "default"
    
    start(ip, int(port), name)