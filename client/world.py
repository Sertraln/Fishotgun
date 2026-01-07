from client.player import Player
from ursina import Vec3

class World:

    def __init__(self):
        self.players: dict[int,Player] = {}
        pass

    def spawn_player(self,player_id:int,name:str,position:Vec3):
        new_player = Player(name=name,position=position)
        self.players[player_id] = new_player