from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

player_map = {}

class ThirdPersonController(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera_offset = -5
        self.body = Entity(
            parent=self,
            model='cube',
            scale=(1,1.5,1),
            y=0.75)
        
        camera.z = self.camera_offset
        camera.collider = 'box'
        # Additional third person setup can go here

    def update(self):
        super().update()
        # Additional third person update can go here
    
    def set_id(self, id: int):
        self.player_id = id
        player_map[id] = self

class Player(Entity):
    def __init__(self, id : int):
        super().__init__()
        self.model = 'cube'
        self.color = color.violet
        self.scale=(1,1.5,1),
        self.player_id = id

def get_player(id: int):
    return player_map.get(id)
        