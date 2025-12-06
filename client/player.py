from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from client.packet.serverbound import ServerBoundMovementPacket
import threading as th
from queue import Queue
from shared.parsedata.input import KeyStates

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
        self._wating_response_queue = Queue()
        self._last_input = KeyStates()
        th.Thread(target=self.constant_update, daemon=True).start()

        # Additional third person setup can go here

        # Physique
        self.vitesse = Vec3(0, 0, 0)
        self.acceleration = Vec3(0, 0, 0)
        self.gravity = -9.8

    def update(self):
        #super().update()
        self.update_pos(self._last_input)
        # Additional third person update can go here

        

    def input(self, key):
        # make key configurable later
        key_strokes:KeyStates = KeyStates(time_stamp=time.time())
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
        self._input_queue.put(key_strokes)
        self._last_input = key_strokes
        
    def _calculate_speed(self,key_strokes:KeyStates):
        if key_strokes.is_pressed(KeyStates.SPRINT):
            return 1.3
        else:
            return 1

    def update_pos(self, key_strokes:KeyStates):
        dt = time.dt
        self.acceleration = Vec3(0, 0, 0)
        self.acceleration.y += self.gravity

        self.speed = self._calculate_speed(key_strokes)
        direction = key_strokes.get_direction() * self.speed
        self.acceleration += direction

        self.vitesse = self.vitesse *0.91 * + 0.1 * self.acceleration

        self.vitesse += self.acceleration * dt
        self.position += self.vitesse * dt

        if self.y < 0:
            self.y = 0
        self.vitesse.y = 0



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
        

    

        