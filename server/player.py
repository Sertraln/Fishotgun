class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.is_connected = True
        self.initialised = False

    def disconnect(self):
        self.is_connected = False

    def get_player(player_id):
        # Placeholder for retrieving a player instance by ID
        pass

    def initialise(self, name: str):
        self.name = name
        self.initialised = True
        