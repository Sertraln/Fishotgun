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

    def __init__(self, key_states:int = 0, time_stamp:float = -1.0, rotation_y:float = 0.0, camera_pitch:float = 0.0):
        self.key_states = key_states
        self.time_stamp = time_stamp
        self.rotation_y = rotation_y      # Rotation horizontale du joueur
        self.camera_pitch = camera_pitch  # Inclinaison de la caméra (haut/bas)

    def is_pressed(self, key:int) -> bool:
        return (self.key_states & key) != 0
    
    def press(self, key:int):
        self.key_states |= key

    def get_direction(self,forward:Vec3,right:Vec3) -> Vec3:
        x, z = 0, 0
        if self.is_pressed(self.FORWARD):
            x += 1
        if self.is_pressed(self.BACKWARD):
            x -= 1
        if self.is_pressed(self.LEFT):
            z -= 1
        if self.is_pressed(self.RIGHT):
            z += 1
        if x != 0 and z != 0:
            x *= 0.7071
            z *= 0.7071
        return x * forward + z * right
    
    def empty(self) -> bool:
        return self.key_states == 0
    
    def __repr__(self):
        return f"KeyStates(key_states={format(self.key_states, '08b')}, time_stamp={self.time_stamp}, rot_y={self.rotation_y:.2f}, pitch={self.camera_pitch:.2f})"
    
    def __eq__(self, other):
        if not isinstance(other, KeyStates):
            return False
        return (self.key_states == other.key_states and 
                abs(self.rotation_y - other.rotation_y) < 0.1 and
                abs(self.camera_pitch - other.camera_pitch) < 0.1)
    
    @staticmethod
    def encode(states: 'KeyStates') -> bytes:
        import struct
        # 1 byte pour key_states + 4 bytes float pour rotation_y + 4 bytes float pour camera_pitch
        return states.key_states.to_bytes(1, 'big') + struct.pack('!ff', states.rotation_y, states.camera_pitch)
    
    @staticmethod
    def decode(data: bytes) -> 'KeyStates':
        import struct
        key_states = int.from_bytes(data[0:1], 'big')
        rotation_y, camera_pitch = struct.unpack('!ff', data[1:9])
        return KeyStates(key_states, rotation_y=rotation_y, camera_pitch=camera_pitch)
