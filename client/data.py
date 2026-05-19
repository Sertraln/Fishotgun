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