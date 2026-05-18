from ursina import *
from direct.actor.Actor import Actor
from client.packet.serverbound import ServerBoundMovementPacket,ServerBoundRotationPacket
import threading as th
from shared.parsedata.input import KeyStates
from client import menu
from shared.movement import Physic
from client import data
import time
import collections
import math

class Player(Entity):
    def __init__(self, id : int, name : str, position :Vec3 = Vec3(0,0,0)):
        super().__init__()
        self._position_tracking_ready = False
        self._suppress_position_rotation = False
        self.position = position
        self.name = name
        self.actor = Actor("assets/models/player/player.glb")
        self.actor.reparent_to(self)
        self.scale = Vec3(1,1.5,1)
        self.player_id = id

        self._auto_face_movement = True
        self._turn_lerp_speed = 8.0
        self._rotation_y_offset = 180.0
        self._min_turn_distance = 0.02
        self._min_angle_delta = 0.5
        self._snap_angle_delta = 0.2
        self._movement_target_rotation_y = self._get_model_rotation_y()
        
        # Interpolation attributes
        self.target_position = position
        self.target_rotation = 0
        self.interpolation_start_time = 0
        self.interpolation_duration = 0.05  # 50ms to match server tickrate
        self._position_tracking_ready = True
    
    def update(self):
        current_time = time.time()
        elapsed = current_time - self.interpolation_start_time
        
        if elapsed < self.interpolation_duration and self.interpolation_duration > 0:
            t = elapsed / self.interpolation_duration
            self.position = lerp(self.position, self.target_position, t)

        self._update_smooth_movement_rotation()

    def __setattr__(self, key, value):
        if key == 'position' and getattr(self, '_position_tracking_ready', False) and not getattr(self, '_suppress_position_rotation', False):
            previous = Vec3(self.position)
            super().__setattr__(key, value)
            self._update_rotation_target_from_movement(previous, Vec3(value))
            return
        super().__setattr__(key, value)

    def _set_position_without_rotation_update(self, position: Vec3):
        self._suppress_position_rotation = True
        try:
            self.position = position
        finally:
            self._suppress_position_rotation = False

    def _update_rotation_target_from_movement(self, previous_position: Vec3, new_position: Vec3):
        if not self._auto_face_movement:
            return

        move_delta = Vec3(new_position.x - previous_position.x, 0, new_position.z - previous_position.z)
        if move_delta.length() <= self._min_turn_distance:
            return

        # Model forward is aligned on Z; X needs opposite sign to match right/left turns.
        desired_rotation = math.degrees(math.atan2(-move_delta.x, move_delta.z)) + self._rotation_y_offset
        angle_delta = abs((desired_rotation - self._movement_target_rotation_y + 180.0) % 360.0 - 180.0)
        if angle_delta < self._min_angle_delta:
            return

        self._movement_target_rotation_y = desired_rotation

    def _update_smooth_movement_rotation(self):
        if not self._auto_face_movement:
            return

        alpha = clamp(time.dt * self._turn_lerp_speed, 0.0, 1.0)
        current = self._get_model_rotation_y()
        next_rotation = lerp_angle(current, self._movement_target_rotation_y, alpha) - 180
        remaining = abs((self._movement_target_rotation_y - next_rotation) % 360.0)
        if remaining < self._snap_angle_delta:
            next_rotation = self._movement_target_rotation_y
        self._set_model_rotation_y(next_rotation)

    def _get_model_rotation_y(self) -> float:
        if hasattr(self, 'actor') and self.actor:
            return self.actor.get_h() + 180.0
        return 0.0

    def _set_model_rotation_y(self, value: float):
        if hasattr(self, 'actor') and self.actor:
            self.actor.set_h(value)
    
    def set_target_position(self, position: Vec3):
        """Start interpolation to target position"""
        self.target_position = position
        self.interpolation_start_time = time.time()
    
    def set_target_rotation(self, rotation: float):
        """Start interpolation to target rotation"""
        self.target_rotation = rotation
        self._movement_target_rotation_y = rotation
        self.interpolation_start_time = time.time()


class ThirdPersonController(Player):
    def __init__(self,id:int, name :str, position:Vec3 = Vec3(0,0,0)):
        super().__init__(id,name,position)
        self.name = "ThirdPersonController"
        self._auto_face_movement = True
        self.physic = Physic(scene,position)
        # L'enregistrement dans le world se fait via World.__init__ qui ajoute player_entity
        self.player_id = id
        self.username = name
        self.cursor = Entity(parent=camera.ui)
        self.height = 2
        self.camera_pivot = Entity(parent=self,y=self.height)
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)
        self.camera_offset = -5
        self._attach_camera_to_pivot()
        self._queue_pos = collections.deque()
        self._dt_last_input = 0
        self._latest_server_state = None
        self._server_state_lock = th.Lock()
        self._last_input = KeyStates()
        self._max_prediction_history = 256
        self._hard_snap_distance = 4.0
        self._reconcile_speed = 100.0
        #th.Thread(target=self.constant_update, daemon=True).start()
        self.on_destroy = self.on_disable
        self.actor.loop('reste')
        self.actor.setPlayRate(1.5,'walk')

    def _attach_camera_to_pivot(self):
        # Reset scale before parenting to avoid cumulative stretch across reconnects.
        camera.scale = Vec3(1, 1, 1)
        camera.parent = self.camera_pivot
        camera.position = Vec3(0, 0, self.camera_offset)
        camera.rotation = Vec3(0, 0, 0)
        

    def update(self):
        #super().update()
        if menu._currentMenu is not None:
            return
        self.update_cam()
        self.update_mouv_input()
        self.update_pos(self._last_input)
        self.reconcile_position_with_server()
        self._update_smooth_movement_rotation()
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
                self._set_position_without_rotation_update(corrected_position)
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
        self._set_position_without_rotation_update(corrected_position)
        self.physic.position = corrected_position
        
    def update_pos(self, key_strokes:KeyStates):
        # Synchroniser la rotation avec la physique pour que forward/right soient corrects
        self.physic.rotation_y = self.camera_pivot.rotation_y
        self.physic.update_phy(time.dt,key_strokes)
        self.position = self.physic.position
        self._queue_pos.append((time.time_ns(), Vec3(self.position)))
        while len(self._queue_pos) > self._max_prediction_history:
            self._queue_pos.popleft()

    def update_cam(self):
        self.camera_pivot.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
        if mouse.velocity[0] != 0:
            data.network.send(ServerBoundRotationPacket(self.camera_pivot.rotation_y,time.time_ns()))
        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

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
            if key_strokes.is_idle():
                self.play_idle_animation()
            elif self._last_input.is_idle():
                self.play_walk_animation()
            self._last_input = key_strokes
            self._last_input_time = time.time_ns()
            self._send_input()

    def on_enable(self):
        mouse.locked = True
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.enabled = True
        if hasattr(self, 'camera_pivot'):
            self._attach_camera_to_pivot()
    
    def on_disable(self):
        mouse.locked = False
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.enabled = False
        self._original_camera_transform = camera.transform  # store original position and rotation
        camera.world_parent = scene
        camera.scale = Vec3(1, 1, 1)

    def play_walk_animation(self):
        if hasattr(self.actor, 'loop'):
            self.actor.play('rest_to_walk')
            invoke(self.play_conditional,'walk',delay=0.2)
    
    def play_idle_animation(self):
        if hasattr(self.actor, 'loop'):
            self.actor.play('walk_to_rest')
            invoke(self.play_conditional,'reste',delay=0.2)
    
    def play_conditional(self,animation:str):
        if not self._last_input.is_idle() and animation == 'walk':
            self.actor.loop('walk')
        elif self._last_input.is_idle() and animation == 'reste':
            self.actor.loop('reste')

    #probably useless but keep for now
    def constant_update(self):
        return
        while True:
            time.sleep(0.05)
        
    def _send_input(self):
        new_packet = ServerBoundMovementPacket(self._last_input, self._last_input_time)
        data.network.send(new_packet)
    
        

    

        