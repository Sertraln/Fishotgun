from client.player import Player,ThirdPersonController
from ursina import Vec3
import threading
import shared.world as world
from client import data

class World:

    def __init__(self):
        self.players: dict[int,Player] = {}
        self.player_init = threading.Event()
        if hasattr(world, 'ground'):
            world.ground.texture = 'assets/textures/grass.png'
            world.ground.texture_scale = (512,512)

    def spawn_player(self,player_id:int,name:str,position:Vec3,rotation:float=0):
        print(f"World: spawning player {player_id} at {position}")
        if hasattr(data, 'network') and data.network and player_id == data.network.id:
            new_player = ThirdPersonController(player_id, name, position)
            data.player = new_player
            self.player_init.set()
        else:
            new_player = Player(player_id, name, position)
        new_player.rotation_y = rotation
        self.players[player_id] = new_player

    def leave_player(self,player_id:int):
        print("client : player leave get :",player_id, flush=True)
        if player_id in self.players:
            del self.players[player_id]