from dataclasses import dataclass
from ursina import Vec3

@registerClass('Player')
@dataclass
class Player:
    name: str
    position: Vec3