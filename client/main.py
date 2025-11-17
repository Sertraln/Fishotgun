from ursina import *
from player import ThirdPersonController
from spot import FishingSpot

app = Ursina()

# Create ground
ground = Entity(
    model='cube',
    scale=(100,10,100),
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
    direction = camera.forward * -1
    offset_clipping = 0.05
    hit_camera = raycast(player.camera_pivot.world_position,direction,-player.camera_offset+offset_clipping,ignore=[player,player.body,camera,spot])
    if hit_camera.hit :
        print(hit_camera.distance,hit_camera.point)
        camera.z_setter(-hit_camera.distance+offset_clipping)
    else:
        camera.z_setter(player.camera_offset)


app.run()