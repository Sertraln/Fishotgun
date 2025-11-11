from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

ground = Entity(
    model='plane',
    scale=(100,1,100),
    texture='grass',
    texture_scale=(10,10),
    collider='box')

player = FirstPersonController(
    model='sphere',
    color=color.blue,
    scale_y=2,
    position=(0,1,0))

app.run()