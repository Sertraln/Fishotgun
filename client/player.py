from ursina import *
from client.packet.serverbound import ServerBoundMovementPacket,ServerBoundRotationPacket
import threading as th
from shared.parsedata.input import KeyStates
from shared.movement import Physic
from client import data
import time
import collections

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
        
        # Interpolation attributes
        self.target_position = position
        self.target_rotation = 0
        self.interpolation_start_time = 0
        self.interpolation_duration = 0.05  # 50ms to match server tickrate
    
    def update(self):
        current_time = time.time()
        elapsed = current_time - self.interpolation_start_time
        
        if elapsed < self.interpolation_duration and self.interpolation_duration > 0:
            t = elapsed / self.interpolation_duration
            self.position = lerp(self.position, self.target_position, t)
            self.rotation_y = lerp(self.rotation_y, self.target_rotation, t)
    
    def set_target_position(self, position: Vec3):
        """Start interpolation to target position"""
        self.target_position = position
        self.interpolation_start_time = time.time()
    
    def set_target_rotation(self, rotation: float):
        """Start interpolation to target rotation"""
        self.target_rotation = rotation
        self.interpolation_start_time = time.time()


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
        self._queue_pos = collections.deque()
        self._dt_last_input = 0
        self._latest_server_state = None
        self._server_state_lock = th.Lock()
        self._last_input = KeyStates()
        self._max_prediction_history = 256
        self._hard_snap_distance = 4.0
        self._reconcile_speed = 100.0
        th.Thread(target=self.constant_update, daemon=True).start()
        self.on_destroy = self.on_disable
        

    def update(self):
        #super().update()
        self.update_cam()
        self.update_mouv_input()
        self.update_pos(self._last_input)
        self.reconcile_position_with_server()
        # Additional third person update can go here

    def register_server_pos(self, timestamp: int, position: Vec3):
        with self._server_state_lock:
            self._latest_server_state = (timestamp, Vec3(position))

    def reconcile_position_with_server(self):
        with self._server_state_lock:
            server_state = self._latest_server_state
            self._latest_server_state = None

        if server_state is None:
            return

        # Use only the latest authoritative state received since last frame.
        server_time, server_position = server_state

        if self._queue_pos:
            # Drop very old history entries (older than 500ms) to keep matching stable.
            history_window_ns = 500_000_000
            while self._queue_pos and self._queue_pos[0][0] < server_time - history_window_ns:
                self._queue_pos.popleft()

            predicted_at_server_time = min(
                self._queue_pos,
                key=lambda sample: abs(sample[0] - server_time)
            )[1]
        else:
            predicted_at_server_time = Vec3(self.position)

        # Error between what server says and what the client predicted at that same time.
        correction = server_position - predicted_at_server_time
        correction_distance = correction.length()

        # Si aucun input en cours, on colle exactement à l'autorité serveur
        if self._last_input.is_idle():
            if correction_distance > 0.001:
                corrected_position = Vec3(server_position)
                self.position = corrected_position
                self.physic.position = corrected_position
            return

        if correction_distance >= self._hard_snap_distance:
            corrected_position = Vec3(server_position)
            self._queue_pos.clear()
        elif correction_distance > 0.01:
            # Apply smooth correction to avoid visible teleporting on small desync.
            alpha = clamp(time.dt * self._reconcile_speed, 0.0, 0.5)
            corrected_position = lerp(self.position, self.position + correction, alpha)
        else:
            return  # No significant error, no correction needed.
        self.position = corrected_position
        self.physic.position = corrected_position
        
    def update_pos(self, key_strokes:KeyStates):
        # Synchroniser la rotation avec la physique pour que forward/right soient corrects
        self.physic.rotation_y = self.rotation_y
        self.physic.update_phy(time.dt,key_strokes)
        self.position = self.physic.position
        self._queue_pos.append((time.time_ns(), Vec3(self.position)))
        while len(self._queue_pos) > self._max_prediction_history:
            self._queue_pos.popleft()

    def update_cam(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
        if mouse.velocity[0] != 0:
            data.network.send(ServerBoundRotationPacket(self.rotation_y,time.time_ns()))
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
        

    

        