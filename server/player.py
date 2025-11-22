from client import Client


class Player:
    def __init__(self, player_name:str, client: Client):
        self.player_id = player_name
        self.client = client
        
