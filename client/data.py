
from client.player import ThirdPersonController
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.network import Network

player = ThirdPersonController(
    position=(0,4,0),
    jump_height = 5,
    jump_up_duration = 1,
    fall_after = .4,
    gravity = 0.7)

network : Network = None