from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from client.packet.serverbound import ServerBoundMovementPacket
import threading as th
from queue import Queue
from shared.parsedata.input import KeyStates

player_map = {}

class ThirdPersonController(Entity):
    def __init__(self,position:Vec3 = Vec3(0,0,0)):
        super().__init__()
        
        self.cursor = Entity(parent=camera.ui)
        self.height = 2
        self.camera_pivot = Entity(parent=self,y=self.height)
        camera.parent = self.camera_pivot
        camera.position = Vec3.zero
        camera.rotation = Vec3.zero
        camera.fov = 90
        mouse.locked = True

        self.mouse_sensitivity = Vec2(40, 40)
        self.camera_offset = -5
        self.body = Entity(
            parent=self,
            model='cube',
            scale=(1,1.5,1),
            y=0.75)
        camera.z = self.camera_offset
        self._input_queue = Queue()
        self._wating_response_queue = Queue()
        self._last_input = KeyStates()
        th.Thread(target=self.constant_update, daemon=True).start()
        self.position = position
        # Additional third person setup can go here
        self.grounded = False
        self.jump_height = 0.3
        self.air_time = 0
        self.speed = 3
        # Physique
        self.vitesse = Vec3(0, 0, 0)
        self.acceleration = Vec3(0, 0, 0)
        self.gravity = -0.6
        self.ignore_list = [self,]
        self.traverse_target = scene

        self.on_destroy = self.on_disable
        

    def update(self):
        #super().update()
        self.update_cam()
        self.update_mouv_input()
        self.update_pos(self._last_input)
        # Additional third person update can go here

    def update_cam(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)
        

    def update_mouv_input(self):
        # make key configurable later
        key_strokes:KeyStates = KeyStates(time_stamp=time.time())
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
        self._input_queue.put(key_strokes)
        self._last_input = key_strokes
        
    def _calculate_speed(self,key_strokes:KeyStates):
        if key_strokes.is_pressed(KeyStates.SPRINT):
            return 1.6
        else:
            return 1
        
    def colision(self, move_amount:Vec3):
        feet_ray = raycast(self.position+Vec3(0,0.5,0), move_amount, traverse_target=self.traverse_target, ignore=self.ignore_list, distance=.5, debug=False)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), move_amount, traverse_target=self.traverse_target, ignore=self.ignore_list, distance=.5, debug=False)
        if not feet_ray.hit and not head_ray.hit:
            if raycast(self.position+Vec3(-.0,1,0), Vec3(1,0,0), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[0] = min(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(-1,0,0), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[0] = max(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,1), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[2] = min(move_amount[2], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,-1), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[2] = max(move_amount[2], 0)
            self.position += move_amount

    def update_pos(self, key_strokes:KeyStates):
        dt = time.dt
        self.acceleration = Vec3(0, 0, 0)
        self.acceleration.y += self.gravity * dt
        if self.grounded:
            self.air_time = 0
            if key_strokes.is_pressed(KeyStates.JUMP):
                self.acceleration.y =self.jump_height
                self.grounded = False

        self.speed = self._calculate_speed(key_strokes)
        air_reducion = 0.3 if not self.grounded else 1
        direction = key_strokes.get_direction(self.forward,self.right) * self.speed * air_reducion * dt * 1.5
        self.acceleration += direction
        if direction != Vec3(0,0,0):
            print("acceleration :",self.acceleration," direction :",
                  direction, " speed :",self.speed,"vitesse :",self.vitesse,"speed:",self.speed)
        self.vitesse = self.vitesse + self.acceleration  

        friction_factor = pow(0.0002, dt)
        air_friction_factor = pow(0.1, dt)
        if not self.grounded:
            friction_factor = air_friction_factor
            self.vitesse.y *= 0.98  # Simulate air resistance on vertical movement
        self.vitesse.x *= friction_factor
        self.vitesse.z *= friction_factor
        if not self.grounded:
            self.air_time += dt
            print(self.vitesse.y,self.position.y)
        #self.colision(self.vitesse)
        self.position += self.vitesse
        if self.y < 0:
            self.y = 0
            self.grounded = True
            self.vitesse.y = 0


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
        

    

        