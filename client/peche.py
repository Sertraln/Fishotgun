from ursina import *
from fish import *
from random import *

app = Ursina()
camera.position=(0,40,0)
camera.rotation=(90,0,0)
camera.fov=40
# editor_camera = EditorCamera(enabled = True)


def update():

    # print(f"pos:({int(camera.position.x)}, {int(camera.position.y)}, {int(camera.position.z)}) - rotation:({int(camera.rotation.x)}, {int(camera.rotation.y)}, {int(camera.rotation.z)})")


    p_pos = point.position
    f_pos = fish.position
    z = (p_pos[0]-f_pos[0],p_pos[2]-f_pos[2])
    p_angle = arg(z)
    if fish.look_at(p_angle):
        point.position=(randrange(-5,5),0,randrange(-5,5))
    

    # # Tourne le poisson sur lui même en boucle
    # fish.set_rotation(fish.angle+0.5)

    # print(fish.angle)
    # if fish.angle==0 : print("Tour complet !")


# cube=Entity(model="cube", color=color.peach, scale=(2,2,2),)
# cube.position=(0,0,0)

# Create a fish
fish = Fish(position=(0,0,0))
referentiel = Entity(model="sphere", color=color.red, scale=(0.5,0.5,0.5))
referentiel.position=(1,0,0)
point = Entity(model="sphere", color=color.salmon, scale=(1,1,1))
point.position=(-2,0,0)

app.run()