from typing import TYPE_CHECKING
from ursina import application,Path,Audio
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for Nuitka/PyInstaller """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller bundle
        base_path = sys._MEIPASS
        return os.path.join(base_path, relative_path)
    elif getattr(sys, 'frozen', False):
        # Nuitka bundle
        base_path = os.path.dirname(sys.executable)
        return os.path.join(base_path, relative_path)
    else:
        # Development mode
        return os.path.join('client', relative_path)

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

#Audios
main_theme = Audio(
    resource_path("assets/musics/fishotgun_main_theme.wav"),
    # "assets/musics/shot.wav",
    loop=True,
    autoplay=False,
    volume=0.6,
    ignore_paused=True
)
life_is_awesome = Audio(
    resource_path("assets/musics/life_is_awesome.wav"),
    autoplay=False,
    loop=True,
    volume=0.4,
    ignore_paused=True
)
birds = Audio(
    resource_path("assets/musics/birds.wav"),
    autoplay=False,
    loop=True,
    volume=0.2,
    ignore_paused=True
)

#const
fisho_font = resource_path("assets/font/FishoFont.ttf")
default_vertex = '''
#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;

varying vec2 uv;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uv = p3d_MultiTexCoord0;
}
'''

# Data folder for user saves (not in assets, which is read-only)
if getattr(sys, 'frozen', False):
    # Compiled: store in user's AppData/Local
    dataPath = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Fishotgun", "data")
else:
    # Development: store in project's data folder
    dataPath = "data"

dataName = "main.dat"
total_path = os.path.join(dataPath, dataName)

def init():
    Path(dataPath).mkdir(parents=True, exist_ok=True)