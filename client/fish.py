from ursina import *
from math import pi,atan2,sqrt,degrees,sin,cos
from random import randrange

Y_OFFSET = -30

def get_angle(dx, dz):
    return (-degrees(atan2(dz, dx))) % 360


class Fish(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'plane'
        self.texture = 'textures/fish_shadow.png'
        self.speedrot = 70
        self.speed = 2
        self.angle = 0
        self.collider = 'box'

    def set_rotation(self, angle: float):
        self.angle = angle%360
        self.rotation = (0, angle, 0)

    def look_at(self, target_pos, catch_radius: float=1.2) -> bool:
        dx = target_pos[0] - self.position[0]
        dz = target_pos[2] - self.position[2]
        dist = sqrt(dx**2 + dz**2)
        if dist < catch_radius: # S'il est trop près (pour éviter de tourner en rond)
            return True
        p_angle = get_angle(dx, dz)
        self.angle = round(self.angle, 1)
        dif = self.angle - p_angle
        self.position = (
            self.position[0] + ((cos(-self.angle*pi/180) * self.speed) * time.dt),
            self.position[1],
            self.position[2] + ((sin(-self.angle*pi/180) * self.speed) * time.dt))
        speed = (self.speedrot + (abs(dif) / 1.5)) * time.dt
        if abs(dif) < speed and dist < catch_radius * 6: # Si le poisson est assez près et vise le rond on change la pos
            return True
        if dif < 0 and dif >= -180 or dif >= 180:
            self.set_rotation(self.angle + speed)
        else:
            self.set_rotation(self.angle - speed)
        return False


class FishingScene:
    def __init__(self, on_end=None):
        self.on_end = on_end
        self.enabled = False
        self._entities = []
        self._fish = None
        self._point = None

    def start(self):
        self.enabled = True
        self._saved_cam_pos = camera.position
        self._saved_cam_rot = camera.rotation
        self._saved_cam_fov = camera.fov

        camera.position = (0, Y_OFFSET, 0)
        camera.rotation = (90, 0, 0)
        camera.fov = 60

        water = Entity(model='plane', color=color.cyan.tint(-0.3), scale=40, position=(0, Y_OFFSET-20, 0), rotation=(0, 0, 0), collider='box')
        fish = Fish(position=(0, Y_OFFSET-19, 0), rotation=(0, 0, 0))
        fish.on_click = self.stop
        point = Entity(model='sphere', color=color.salmon, scale=0.5, position=(2, Y_OFFSET-19, 2))

        self._fish = fish
        self._point = point
        self._entities = [water, fish, point]

    def update(self):
        if not self.enabled or not self._fish or not self._point:
            return
        if self._fish.look_at(self._point.position):
            self._point.position = (randrange(-11, 11), Y_OFFSET-19, randrange(-6, 6))

    def stop(self):
        if not self.enabled:
            return
        self.enabled = False
        camera.position = self._saved_cam_pos
        camera.rotation = self._saved_cam_rot
        camera.fov = self._saved_cam_fov
        for e in self._entities:
            destroy(e)
        self._entities = []
        self._fish = None
        self._point = None
        if self.on_end:
            self.on_end('caught')