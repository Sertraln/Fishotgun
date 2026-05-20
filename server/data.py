from typing import TYPE_CHECKING
from ursina import Vec3
from pathlib import Path

if TYPE_CHECKING:
    from server.main import Server

server : 'Server' = None
dataPath = "data/"
default_pos = Vec3(0,10,0)

def init_data():
    Path(dataPath).mkdir(parents=True, exist_ok=True)