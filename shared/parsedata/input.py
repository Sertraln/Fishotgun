from shared.parser import Parser
from shared.packetlib import register_parser
from ursina import Vec3


@register_parser
class KeyStates(Parser):
    FORWARD = 0x01
    BACKWARD = 0x02
    LEFT = 0x04
    RIGHT = 0x08
    JUMP = 0x10
    SNEAK = 0x20
    SPRINT = 0x40

    def __init__(self, key_states:int = 0,time_stamp:float = 0.0):
        self.key_states = key_states
        self.time_stamp = time_stamp

    def is_pressed(self, key:int) -> bool:
        return (self.key_states & key) != 0
    
    def press(self, key:int):
        self.key_states |= key

    def get_direction(self) -> tuple[int, int]:
        x, z = 0, 0
        if self.is_pressed(self.FORWARD):
            z += 1
        if self.is_pressed(self.BACKWARD):
            z -= 1
        if self.is_pressed(self.LEFT):
            x -= 1
        if self.is_pressed(self.RIGHT):
            x += 1
        if x != 0 and z != 0:
            x *= 0.7071
            z *= 0.7071
        return Vec3(x,0, z)
    
    @staticmethod
    def encode(states: 'KeyStates') -> bytes:
        return states.key_states.to_bytes(1, 'big')
    
    @staticmethod
    def decode(data: bytes) -> 'KeyStates':
        return KeyStates(int.from_bytes(data, 'big'))
