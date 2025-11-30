from ursina import *
from player import ThirdPersonController
from spot import FishingSpot

app = Ursina()

# Create ground
ground = Entity(
    model='cube',
    scale=(100,1,100),
    texture='grass',
    texture_scale=(10,10),
    collider='box')

# Create player
player = ThirdPersonController(
    position=(0,4,0))

# Set cursor white cause pink ugly af
player.cursor.color = color.white


# Create a fishing spot
spot = FishingSpot(position=(0,2,0))


# Set basic sky
Sky(color=color.violet)

def update():
    # apres une dure labeure, la premiere methode a echoue mais je reviens plus fort promis

    # Make player respawn if he falls
    if player.y < -10:
        player.position = (0,4,0)
    
    # Kick player if flies example
    if player.air_time > 10:
        pass

    # Kick player if too fast
    if player.speed > 21:
        pass
    
    # Gotta check this for all spots in the map constantly (will need a list later)
    if distance(spot.position, player.position) < spot.interaction_range:
        if held_keys['e']:
            spot.interact()
        else: 
            spot.color = color.white
    else:
        spot.color = color.white

app.run()