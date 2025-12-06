
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from player import ThirdPersonController
    from network import Network
    from ursina import Ursina

player : 'ThirdPersonController' = None
network : 'Network' = None
app : 'Ursina' = None