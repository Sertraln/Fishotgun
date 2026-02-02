
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client.player import ThirdPersonController
    from client.network import Network
    from ursina import Ursina,Entity,Text
    from client.world import World
    from shared.world import WorldScene

player : 'ThirdPersonController' = None
network : 'Network' = None
app : 'Ursina' = None
spot : 'Entity' = None
instructions : 'Text' = None
world : 'World' = None
world_scene : 'WorldScene' = None