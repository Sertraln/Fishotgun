from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Create ground
ground = Entity(
    model='cube',
    scale=(100,1,100),
    texture='grass',
    texture_scale=(10,10),
    collider='box')

# Create player
player = FirstPersonController(
    position=(0,4,0),
    jump_height = 8,
    gravity = 2.5)

# Set cursor white cause pink ugly af
player.cursor.color = color.white

# Create its shape (body)
body = Entity(
    parent=player,
    model='cube',
    scale=(1,1.5,1),
    y=0.75
)

# Set third person
camera.z = -5

# Set basic sky
Sky(color=color.violet)

def update():
    # Make player respawn if he falls
    if player.y < -20:
        player.position = (0,4,0)
    
    # Sprints if shift is held
    if held_keys['shift']:
        body.color = color.red
        player.speed = 20
    else:
        body.color = color.blue
        player.speed = 10

app.run()