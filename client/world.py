from client.player import Player,ThirdPersonController
from ursina import Vec3
import threading

class World:

    def __init__(self):
        self.players: dict[int,Player] = {}
        self.player_init = threading.Event()

    def spawn_player(self,player_id:int,name:str,position:Vec3):
        print(f"World: spawning player {player_id} at {position}")
        new_player = Player(player_id,name=name,position=position)
        self.players[player_id] = new_player

    def leave_player(self,player_id:int):
        print("client : player leave get :",player_id, flush=True)
        if player_id in self.players:
            del self.players[player_id]