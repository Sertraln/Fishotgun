from ursina import *
from math import pi,cos,sin,acos,sqrt
from noise import *

def rad_to_deg(angle):
    return angle*180/pi

def arg(z):
    x,y=z
    return acos(x/sqrt(x**2+y**2))

class Fish(Entity):
    def __init__(self, **kwargs):  # <- c'est quoi "Kwargs" ?
        super().__init__(**kwargs)
        self.model = 'cube'
        self.position=(0,0,0)
        self.color = color.peach
        self.speed = 2
        self.angle = 0    
    
    def set_rotation(self,angle):
        # if angle>=0:
        #     angle %=360
        # else:
        #     angle = (360+angle)%360

        # # angle = (360+angle)%360
        self.angle = angle
        self.rotation = (0,angle,0)

    def look_at(self,p_angle): # point -> (x,y,z)
        # p_angle = round(rad_to_deg(arg((point[0],point[2]))),1)
        self.angle = round(self.angle,1)
        dif = self.angle-p_angle
        print(f"angle:{self.angle}  p_angle:{p_angle}")
        if abs(dif)<self.speed:
            return True
        elif abs(dif)==180:
            self.set_rotation(self.angle + self.speed)
            return False
        else :
            if dif<0:
                self.set_rotation(self.angle + self.speed)
                return False
            else :
                self.set_rotation(self.angle - self.speed)
                return False




# class Fish(Entity):
#     def __init__(self, **kwargs):  # <- c'est quoi "Kwargs" ?
#         super().__init__(**kwargs)
#         self.model = 'cube'
#         self.color = color.peach
#         self.speed = 2
#         self.radius = 1
#         self.direction = 0
#         self.variation = PerlinNoise()
#         self.amplitude = 30

#         # Range to interact for the fishing spot
#         for key, value in kwargs.items():
#             setattr(self, key, value)

#     def deg_to_rad(angle):
#         return angle*pi/180
    



#     def update(self):
        
#         self.direction += self.speed*time.dt
#         var = self.variation.interpolated_noise(self.direction)*30

#         self.x = self.radius*cos(Fish.deg_to_rad(var))
#         self.z = self.radius*sin(Fish.deg_to_rad(var))
#         self.rotation=(0,-(var%360),0)

#         # self.z = var
#         # print(var)

