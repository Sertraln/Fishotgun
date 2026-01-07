from ursina import *
from math import pi,atan,sqrt
# from noise import *


def rad_to_deg(angle):
    return -angle*180/pi

def arg(z)->float:
    """
    arg(z)
    param z: coordonnées (x,y)
    return : argument du (angle entre l'axe des abcisses et le) point z en degré
    """
    x,y=z

    if x==0 : # le point est sur l'axe des ordonnées
              # à vérifier car après on / par x
        if y==0 :
            return 0.0
        if y>0 :
            return 270.0
        return 90.0
    
    hyp = sqrt(x**2+y**2)
    x,y = x/hyp, y/hyp # on ramène les points sur le cercle trigo en gardant le même angle

    if x<0 :
        return round((rad_to_deg(atan(y/x))+180)%360,1)

    return round(rad_to_deg(atan(y/x))%360,1)

class Fish(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'plane'
        self.texture = 'textures/fish_shadow.png'
        self.position=(0,0,0)
        # self.color = color.peach
        self.speed = 2
        self.angle = 0    
    
    def set_rotation(self,angle:int):
        self.angle = angle%360
        self.rotation = (0,angle,0)

    def look_at(self,p_angle:int) -> bool: # point -> (x,y,z)
        # p_angle = round(rad_to_deg(arg((point[0],point[2]))),1)
        self.angle = round(self.angle,1)
        dif = self.angle-p_angle
        #print(f"angle:{self.angle}  p_angle:{p_angle}")
        if abs(dif)<self.speed:
            return True
        
        if dif<0 and dif >=-180 or dif >= 180 : 
            self.set_rotation(self.angle + self.speed)
        else :
            self.set_rotation(self.angle - self.speed)
        return False


