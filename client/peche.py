from ursina import *
from fish import *
from random import *

def update():

    camera.position=(0,40,0)
    camera.rotation=(90,0,0)
    camera.fov=40

    p_pos = point.position
    p_angle = round(rad_to_deg(arg((p_pos[0],p_pos[2]))),1)
    if fish.look_at(p_angle):
        print("------- point found -------")
        point.position=(randrange(-5,5),0,randrange(-5,5))
        while point.position==(0,0,0):
            point.position=(randrange(-5,5),0,randrange(-5,5))


# cube=Entity(model="cube", color=color.peach, scale=(2,2,2),)
# cube.position=(0,0,0)

# Create a fish
fish = Fish(position=(0,0,0))
point = Entity(model="sphere", color=color.salmon, scale=(1,1,1))
point.position=(5,0,5)

app = Ursina()

app.run()