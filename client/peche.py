from ursina import *
from fish import *

def update():

    camera.position=(0,40,0)
    camera.rotation=(90,0,0)
    camera.fov=40


# cube=Entity(model="cube", color=color.peach, scale=(2,2,2),)
# cube.position=(0,0,0)

# Create a fish
fish = Fish(position=(0,0,0))

app = Ursina()

app.run()