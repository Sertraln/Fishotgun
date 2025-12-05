from shared.parser import Parser
from shared.packetlib import register_parser


@register_parser
class KeyStates(Parser):
    FORWARD = 0x01
    BACKWARD = 0x02
    LEFT = 0x04
    RIGHT = 0x08
    JUMP = 0x10
    SNEAK = 0x20
    SPRINT = 0x40

    def __init__(self, key_states:int = 0):
        self.key_states = key_states

    def is_pressed(self, key:int) -> bool:
        return (self.key_states & key) != 0
    
    def press(self, key:int):
        self.key_states |= key
    
    @staticmethod
    def encode(states: 'KeyStates') -> bytes:
        return states.key_states.to_bytes(1, 'big')
    
    @staticmethod
    def decode(data: bytes) -> 'KeyStates':
        return KeyStates(int.from_bytes(data, 'big'))
