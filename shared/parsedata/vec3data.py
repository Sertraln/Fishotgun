from ursina import Vec3
from shared.parser import Wrapper
import struct
from shared.packetlib import register_wrapper

@register_wrapper(Vec3)
class Vec3Data(Wrapper):

    _patern = ">fff"
    size = struct.calcsize(_patern)

    @staticmethod
    def decode(data:bytes) -> Vec3:
        x,y,z = struct.unpack(Vec3Data._patern,data)
        return Vec3(x,y,z)

    @staticmethod
    def encode(vec:Vec3) -> bytes:
        return struct.pack(Vec3Data._patern, vec.x, vec.y, vec.z)
    
