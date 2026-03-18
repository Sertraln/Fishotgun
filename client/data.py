from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client.player import ThirdPersonController
    from client.network import Network
    from ursina import Ursina,Entity,Text
    from client.world import World

player : 'ThirdPersonController' = None
network : 'Network' = None
world_entities : list['Entity'] = []
instructions : 'Text' = None
app : 'Ursina' = None
world : 'World' = None