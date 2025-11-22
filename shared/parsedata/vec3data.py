from ursina import Vec3
from shared.parser import Wrapper

class Vec3Data(Wrapper):

    def __init__(self, wrapped : Vec3):
        self.wrapped = wrapped

    @staticmethod
    def decode(data:str) -> Vec3:
        x,y,z = map(float,data.split(','))
        return Vec3(x,y,z)

    def encode(self,) -> str:
        return f"{self.wrapped[0]},{self.wrapped[1]},{self.wrapped[2]}"
    
