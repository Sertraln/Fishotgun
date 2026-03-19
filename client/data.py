from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client.player import ThirdPersonController
    from client.network import Network
    from ursina import Ursina,Entity,Text
    from client.world import World
    from client.transitions import IrisTransition
    from client.fish import FishingScene

player : 'ThirdPersonController' = None
network : 'Network' = None
world_entities : list['Entity'] = []
instructions : 'Text' = None
app : 'Ursina' = None
world : 'World' = None
iris: 'IrisTransition' = None
fishing_scene: 'FishingScene' = None
