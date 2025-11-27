from ursina import *
from math import pi,cos,sin
from noise import *

class Fish(Entity):
    def __init__(self, **kwargs):  # <- c'est quoi "Kwargs" ?
        super().__init__(**kwargs)
        self.model = 'cube'
        self.color = color.peach
        self.speed = 2
        self.radius = 1
        self.direction = 0
        self.variation = PerlinNoise()
        self.amplitude = 30

        # Range to interact for the fishing spot
        for key, value in kwargs.items():
            setattr(self, key, value)

    def deg_to_rad(angle):
        return angle*pi/180
    
    def rad_to_deg(angle):
        return angle*180/pi


    def update(self):
        
        self.direction += self.speed*time.dt
        var = self.variation.interpolated_noise(self.direction)*30

        self.x = self.radius*cos(Fish.deg_to_rad(var))
        self.z = self.radius*sin(Fish.deg_to_rad(var))
        self.rotation=(0,-(var%360),0)

        # self.z = var
        # print(var)
