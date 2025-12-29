from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from client.packet.serverbound import ServerBoundMovementPacket
import threading as th
from queue import Queue
from shared.parsedata.input import KeyStates
from shared.movement import calculate_safe_movement

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
    def __init__(self,id:int , name :str, position:Vec3 = Vec3(0,0,0)):
        super().__init__(id,name,position)
        self.name = "ThirdPersonController"
        self.cursor = Entity(parent=camera.ui)
        self.height = 2
        self.camera_pivot = Entity(parent=self,y=self.height)
        camera.parent = self.camera_pivot
        camera.fov = 90
        mouse.locked = True

        self.mouse_sensitivity = Vec2(40, 40)
        self.camera_offset = -5
        camera.z = self.camera_offset
        self._input_queue = Queue()
        self._dt_last_input = 0
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
        self.ignore_list = [self]
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
        if key_strokes != self._last_input:
            self._input_queue.put(key_strokes)
            self._last_input = key_strokes
            self._dt_last_input = 0
        else:
            self._dt_last_input += time.dt
        
        
    def _calculate_speed(self,key_strokes:KeyStates):
        if key_strokes.is_pressed(KeyStates.SPRINT):
            return 1.6
        else:
            return 1
        
    def colision(self, move_amount:Vec3,mov_len:float, mov_dir:Vec3):
        #todo: implement a robust colision system
        self.vitesse = calculate_safe_movement(self, move_amount,mov_dir,mov_len, self.traverse_target)

    def update_pos(self, key_strokes:KeyStates):
        dt : float = time.dt
        self.acceleration = Vec3(0, 0, 0)
        self.acceleration.y += self.gravity * dt
        if self.grounded:
            self.air_time = 0
            if key_strokes.is_pressed(KeyStates.JUMP):
                self.acceleration.y =self.jump_height
                self.grounded = False

        self.speed = self._calculate_speed(key_strokes)
        air_reducion = 0.3 if not self.grounded else 1
        mov_dir = key_strokes.get_direction(self.forward,self.right)
        direction : Vec3 = mov_dir * self.speed * air_reducion * dt * 1.5
        self.acceleration += direction
        self.vitesse : Vec3 = self.vitesse + self.acceleration  

        friction_factor = pow(10000, dt)
        air_friction_factor = pow(6, dt)
        if not self.grounded:
            friction_factor = air_friction_factor
            self.vitesse.y *= 0.98  # Simulate air resistance on vertical movement
        self.vitesse.x /= friction_factor
        self.vitesse.z /= friction_factor
        if not self.grounded:
            self.air_time += dt
        self.colision(self.vitesse,self.vitesse.length(),mov_dir)
        self.ground_colision()
        self.position += self.vitesse
        

    def ground_colision(self):
        y_speed = self.vitesse.y
        ground_ray = raycast(self.position+Vec3(0,self.height-0.2,0), Vec3(0,-1,0), distance=self.height-0.2-y_speed, traverse_target=self.traverse_target, ignore=self.ignore_list, debug=False)
        head_ray = raycast(self.position+Vec3(0,0.2,0), Vec3(0,1,0), distance=self.height-0.2+y_speed, traverse_target=self.traverse_target, ignore=self.ignore_list, debug=False)
        if ground_ray.hit and self.vitesse.y <= 0:
            self.grounded = True
            self.y = ground_ray.world_point.y
            self.vitesse.y = 0
        elif head_ray.hit and self.vitesse.y > 0:
            self.vitesse.y = 0
            self.position.y = head_ray.world_point.y - self.height -0.1
        else:
            self.grounded = False

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
        new_packet = ServerBoundMovementPacket(self._input_queue, time.time())
        self.client.send_packet(new_packet)
        pass
    
    def set_id(self, id: int):
        self.player_id = id
        player_map[id] = self



def get_player(id: int):
    return player_map.get(id)
        

    

        