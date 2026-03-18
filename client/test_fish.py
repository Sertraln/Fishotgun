# FICHIER DE TEST POUR PECHE RIEN D'AUTRE

from ursina import *
from fish import *
from random import *

app = Ursina()
camera.position=(0,40,0)
camera.rotation=(90,0,0)
camera.fov=40

def update():
    if fish.look_at(point.position):
        point.position=(randrange(-5,5),0,randrange(-5,5))

    if fish2.look_at(point2.position):
        point2.position=(randrange(-5,5),0,randrange(-5,5))
    
    if fish3.look_at(point3.position):
        point3.position=(randrange(-5,5),0,randrange(-5,5))

fish = Fish(position=(0,0,0))
fish2 = Fish(position=(2,0,2), color=color.azure)
fish3 = Fish(position=(-2,0,-2), color=color.green)
referentiel = Entity(model="sphere", color=color.red, scale=(0.5,0.5,0.5))
referentiel.position=(1,0,0)
point = Entity(model="sphere", color=color.salmon, scale=(1,1,1))
point.position=(0,0,0)
point2 = Entity(model="sphere", color=color.salmon, scale=(1,1,1))
point2.position=(-2,0,0)
point3 = Entity(model="sphere", color=color.salmon, scale=(1,1,1))
point3.position=(2,0,0)

app.run()