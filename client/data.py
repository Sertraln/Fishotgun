
from client.player import ThirdPersonController

player = ThirdPersonController(
    position=(0,4,0),
    jump_height = 5,
    jump_up_duration = 1,
    fall_after = .4,
    gravity = 0.7)