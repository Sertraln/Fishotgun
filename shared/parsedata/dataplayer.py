from dataclasses import dataclass
from ursina import Vec3

@dataclass
class Player:
    name: str
    position: Vec3