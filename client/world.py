from client.player import Player,ThirdPersonController
from ursina import Vec3

class World:

    def __init__(self):
        self.players: dict[int,Player] = {}

    def spawn_player(self,player_id:int,name:str,position:Vec3):
        print(f"World: spawning player {player_id} at {position}")
        new_player = Player(player_id,name=name,position=position)
        self.players[player_id] = new_player