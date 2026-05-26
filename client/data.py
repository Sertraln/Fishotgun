from typing import TYPE_CHECKING
from ursina import application,Path,Audio
if TYPE_CHECKING:
    from client.player import ThirdPersonController
    from client.network import Network
    from ursina import Ursina,Entity,Text
    from client.world import World
    from client.transitions import IrisTransition
    from client.fish import FishingScene
    from client.menus.hud import Hud

player : 'ThirdPersonController' = None
network : 'Network' = None
world_entities : list['Entity'] = []
instructions : 'Text' = None
app : 'Ursina' = None
world : 'World' = None
iris: 'IrisTransition' = None
fishing_scene: 'FishingScene' = None
hud: 'Hud' = None

#Audios
main_theme = Audio(
    "assets/musics/fishotgun_main_theme.wav",
    # "assets/musics/shot.wav",
    loop=True,
    autoplay=False,
    volume=0.6,
    ignore_paused=True
)
life_is_awesome = Audio(
    "assets/musics/life_is_awesome.wav",
    autoplay=False,
    loop=True,
    volume=0.4,
    ignore_paused=True
)
birds = Audio(
    "assets/musics/birds.wav",
    autoplay=False,
    loop=True,
    volume=0.2,
    ignore_paused=True
)

#const
fisho_font = "assets/font/FishoFont.ttf"
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

dataPath = application.asset_folder / "data/"
dataName = "main.dat"
total_path = dataPath / dataName

def init():
    Path(dataPath).mkdir(parents=True, exist_ok=True)