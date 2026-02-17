
class World:
    pass

    def add_entity(self, entity: Entity):
        pass

from client import data,menu,network
from spot import FishingSpot
from ursina import application,Button,Entity,color

def join_world(ip:str, port:int, name:str):
    data.network = network.Network(ip,port,name)
    load_world()

def load_world():
    # Create ground
    ground = Entity(
        model='cube',
        scale=(100,10,100),
        texture='grass',
        texture_scale=(10,10),
        collider='box')
    data.world = World()
    data.world.add_entity(ground)

    from client.data import player
    from client.player import ThirdPersonController

    player = ThirdPersonController(
        position=(0,4,0),
        jump_height = 5,
        jump_up_duration = 1,
        fall_after = .4,
        gravity = 0.7)
    
    data.player = player

    # Set cursor white cause pink ugly af


    # Create a fishing spot
    spot = FishingSpot(position=(0,2,0))

    menu1 = menu.Menu()
    menu1.add_element(Button(text='Resume', scale=(0.3, 0.1), position=(0,0.1)))
    quit =Button(text='Quit', scale=(0.3, 0.1), position=(0,-0.1))
    quit.on_click = application.quit
    menu1.add_element(quit)