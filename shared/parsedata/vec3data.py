from ursina import Vec3
from shared.parser import Wrapper

class Vec3Data(Wrapper):

    @staticmethod
    def decode(data:str) -> Vec3:
        x,y,z = map(float,data.split(','))
        return Vec3(x,y,z)

    @staticmethod
    def encode(vec:Vec3) -> str:
        return f"{vec[0]},{vec[1]},{vec[2]}"
    
