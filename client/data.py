
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from player import ThirdPersonController
    from network import Network
    from world import World

player : 'ThirdPersonController' = None
network : 'Network' = None
world : 'World' = None