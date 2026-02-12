from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from client.packet.serverbound import ServerBoundMovementPacket
import threading as th
from queue import Queue
from shared.parsedata.input import KeyStates
import menu

player_map = {}

class ThirdPersonController(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera_offset = -5
        self.body = Entity(
            parent=self,
            model='cube',
            scale=(1,1.5,1),
            y=0.75)
        
        camera.z = self.camera_offset
        camera.collider = 'box'
        self._input_queue = Queue()
        th.Thread(target=self.constant_update, daemon=True).start()

        # Additional third person setup can go here

    def update(self):
        if menu.ispausing(): return
        super().update()
        # Additional third person update can go here

    def input(self, key):
        # make key configurable later
        key_strokes:KeyStates = KeyStates()
        if key == 'shift':
            key_strokes.press(KeyStates.SPRINT)
        if key == 'space':
            key_strokes.press(KeyStates.JUMP)
        if key == 'w':
            key_strokes.press(KeyStates.FORWARD)
        if key == 's':
            key_strokes.press(KeyStates.BACKWARD)
        if key == 'a':
            key_strokes.press(KeyStates.LEFT)
        if key == 'd':
            key_strokes.press(KeyStates.RIGHT)
        if key == 'control':
            key_strokes.press(KeyStates.SNEAK)
        self.key_states = key_strokes


    def constant_update(self):
        while True:
            self._send_input()
            time.sleep(0.05)
        

    def _send_input(self):
        #new_packet = ServerBoundMovementPacket(self.key_states, time.time())
        #self.client.send_packet(new_packet)
        pass
    
    def set_id(self, id: int):
        self.player_id = id
        player_map[id] = self

class Player(Entity):
    def __init__(self, id : int, name : str, position :Vec3 = Vec3(0,0,0)):
        super().__init__()
        self.position = position
        self.name = name
        self.model = 'cube'
        self.color = color.violet
        self.scale=(1,1.5,1),
        self.player_id = id

def get_player(id: int):
    return player_map.get(id)
        