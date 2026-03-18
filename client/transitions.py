from ursina import *

iris_vertex = '''
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

iris_fragment = '''
#version 120
varying vec2 uv;
uniform float radius;
uniform float aspect;
void main() {
    vec2 centered = vec2((uv.x - 0.5) / (aspect/2), (uv.y - 0.5));
    float dist = length(centered);
    if (dist < radius * 0.7) discard;
    gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
'''

class IrisTransition:
    IDLE    = 0
    CLOSING = 1
    BLACK   = 2
    OPENING = 3

    def __init__(self, close_duration=0.5, black_duration=0.3, open_duration=0.5):
        self.close_duration = close_duration
        self.black_duration = black_duration
        self.open_duration  = open_duration
        self.overlay = Entity(
            parent=camera.ui,
            model='quad',
            scale=2,
            shader=Shader(vertex=iris_vertex, fragment=iris_fragment),
            enabled=False,
            z=-1
        )
        self.overlay.set_shader_input('radius', 1.0)
        self.overlay.set_shader_input('aspect', window.aspect_ratio)
        self._state    = self.IDLE
        self._t        = 0.0
        self._callback = None

    def play(self, on_black=None):
        self._callback = on_black
        self._state    = self.CLOSING
        self._t        = 0.0
        self.overlay.enabled = True
        self.overlay.set_shader_input('radius', 1.0)

    def update(self):
        if self._state == self.IDLE:
            return

        self._t += time.dt

        if self._state == self.CLOSING:
            r = max(0.0, 1.0 - self._t / self.close_duration)
            self.overlay.set_shader_input('radius', r)
            if self._t >= self.close_duration:
                self.overlay.set_shader_input('radius', 0.0)
                if self._callback:
                    self._callback()
                self._state = self.BLACK
                self._t     = 0.0

        elif self._state == self.BLACK:
            if self._t >= self.black_duration:
                self._state = self.OPENING
                self._t     = 0.0

        elif self._state == self.OPENING:
            r = min(1.0, self._t / self.open_duration)
            self.overlay.set_shader_input('radius', r)
            if self._t >= self.open_duration:
                self.overlay.set_shader_input('radius', 1.0)
                self.overlay.enabled = False
                self._state = self.IDLE