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
    position=(0,4,0),
    jump_height = 5,
    jump_up_duration = 1,
    fall_after = .4,
    gravity = 0.7)

# Set cursor white cause pink ugly af
player.cursor.color = color.white


# Create a fishing spot
spot = FishingSpot(position=(0,2,0))


# Set basic sky
Sky(color=color.violet)

def update():
    # Make player respawn if he falls
    if player.y < -10:
        player.position = (0,4,0)
    
    # Kick player if flies example
    if player.air_time > 10:
        pass

    # Kick player if too fast
    if player.speed > 21:
        pass
    
    # Sprints if shift is held
    if held_keys['shift']:
        player.body.color = color.red
        player.speed = 20
    else:
        player.body.color = color.blue
        player.speed = 10
    
    # Gotta check this for all spots in the map constantly (will need a list later)
    if distance(spot.position, player.position) < spot.interaction_range:
        if held_keys['e']:
            spot.interact()
        else: 
            spot.color = color.white
    else:
        spot.color = color.white

    # Check if the camera is clipping anywhere
    hit_camera = camera.intersects()
    if hit_camera:
        camera.set_z(camera.get_z() + 0.1)
    else:
        if camera.get_z() > -5.0:
            camera.set_z(camera.get_z() - 0.1)


app.run()