from ursina import *
from client.packet.serverbound import ServerBoundMovementPacket
import threading as th
from queue import Queue
from shared.parsedata.input import KeyStates
from shared.movement import Physic
from client import data

player_map = {}

class Player(Entity):
    def __init__(self, id : int, name : str, position :Vec3 = Vec3(0,0,0)):
        super().__init__()
        self.position = position
        self.name = name
        self.model = 'cube'
        self._model.setPos(Vec3(0,0.5,0))
        self.color = color.violet
        self.scale = Vec3(1,1.5,1)
        self.player_id = id

class ThirdPersonController(Player):
    def __init__(self,id:int, name :str, position:Vec3 = Vec3(0,0,0)):
        super().__init__(id,name,position)
        self.name = "ThirdPersonController"
        self.physic = Physic(scene,position)
        self.color = color.orange
        # L'enregistrement dans le world se fait via World.__init__ qui ajoute player_entity
        self.player_id = id
        self.username = name
        self.cursor = Entity(parent=camera.ui)
        self.height = 2
        self.camera_pivot = Entity(parent=self,y=self.height)
        camera.parent = self.camera_pivot
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)
        self.camera_offset = -5
        camera.z = self.camera_offset
        self._input_queue = Queue()
        self._dt_last_input = 0
        self._wating_response_queue = Queue()
        self._last_input = KeyStates()
        th.Thread(target=self.constant_update, daemon=True).start()
        self.on_destroy = self.on_disable
        

    def update(self):
        #super().update()
        self.update_cam()
        self.update_mouv_input()
        self.update_pos(self._last_input)
        # Additional third person update can go here

    def update_pos(self, key_strokes:KeyStates):
        # Synchroniser la rotation avec la physique pour que forward/right soient corrects
        self.physic.rotation_y = self.rotation_y
        self.physic.update_phy(time.dt,key_strokes)
        self.position = self.physic.position

    def update_cam(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)
        

    def input(self, key):
        if key == 'escape':
            mouse.locked = not mouse.locked

    def update_mouv_input(self):
        
        
        # make key configurable later
        key_strokes:KeyStates = KeyStates()
        if held_keys['shift']:
            key_strokes.press(KeyStates.SPRINT)
        if held_keys['space']:
            key_strokes.press(KeyStates.JUMP)
        if held_keys['w']:
            key_strokes.press(KeyStates.FORWARD)
        if held_keys['s']:
            key_strokes.press(KeyStates.BACKWARD)
        if held_keys['a']:
            key_strokes.press(KeyStates.LEFT)
        if held_keys['d']:
            key_strokes.press(KeyStates.RIGHT)
        if held_keys['control']:
            key_strokes.press(KeyStates.SNEAK)
        if key_strokes != self._last_input:
            self._input_queue.put(key_strokes)
            self._last_input = key_strokes
            self._last_input_time = time.time_ns()
            self._send_input()

    def on_enable(self):
        mouse.locked = True
        self.cursor.enabled = True
        # restore parent and position/rotation from before disablem in case you moved the camera in the meantime.
        if hasattr(self, 'camera_pivot') and hasattr(self, '_original_camera_transform'):
            camera.parent = self.camera_pivot
            camera.transform = self._original_camera_transform
    
    def on_disable(self):
        mouse.locked = False
        self.cursor.enabled = False
        self._original_camera_transform = camera.transform  # store original position and rotation
        camera.world_parent = scene

    #probably useless but keep for now
    def constant_update(self):
        return
        while True:
            time.sleep(0.05)
        
    def _send_input(self):
        new_packet = ServerBoundMovementPacket(self._last_input, self._last_input_time)
        data.network.send(new_packet)
    
    def set_id(self, id: int):
        self.player_id = id
        player_map[id] = self



def get_player(id: int):
    return player_map.get(id)
        

    

        