from typing import TYPE_CHECKING
from server import data
from server.packet.clientbound import *
import threading as th
import time
from shared import world

from panda3d.bullet import BulletWorld
from panda3d.core import Vec3 as PVec3
import copy

if TYPE_CHECKING:
    from server.player import Player
    from server.entity import Entity
    from shared.parsedata.input import KeyStates
    from server.client import Client

class World:
    def __init__(self):
        self.entities : dict[int,'Entity'] = {}
        self.tickrate = 20
        self.dt_per_tick = 1.0 / self.tickrate
        self.next_entity_id = 0
        self.players : dict[int,'Player'] = {}
        self._lock = th.Lock()

        self.bullet_world = BulletWorld()
        self.bullet_world.setGravity(PVec3(0, 0, -25.0))

        from panda3d.core import NodePath
        _root = NodePath("server_root")
        world.init_world(_root, bullet_world=self.bullet_world)

        print("World: initialized")
        self.last_update_time = time.time()
        th.Thread(target=self._game_loop, daemon=True).start()

    @property
    def world_scene(self):
        return self

    def join_player(self, player:'Player') -> int:
        player.client.send(ClientBoundInitPlayerPacket(player))
        player.client.send(ClientBoundPlayerListPacket(list(self.players.values())))
        pid = player.client.id
        self.players[pid] = player
        print(f"World: player joined {pid}")
        data.server.broadcast(ClientBoundSpawnPlayerPacket(player),[player.client.id]) 
        return pid

    def left_player(self, pid:int):
        if pid in self.players:
            data.server.broadcast(ClientBoundPlayerLeavePacket(pid),[pid])
            player = self.players.pop(pid)
            player.save()
            print(f"World: player left {pid}")

    def stop(self):
        for pid, player in list(self.players.items()):
            try:
                player.client.kick()
            except Exception:
                pass
        self.players.clear()

    def add_entity(self, entity:'Entity') -> int:
        entity_id = self.get_next_entity_id()
        self.entities[entity_id] = entity
        entity.id = entity_id
        return entity_id
    
    def get_next_entity_id(self):
        self.next_entity_id += 1
        return self.next_entity_id
    
    def _game_loop(self):
        while True:
            dt = self.dt()
            self.last_update_time = time.time()
            self.game_loop(dt)
            ending_dt = self.dt()
            sleep_time = self.dt_per_tick - ending_dt
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                print("World: Warning - game loop is taking longer than tick interval")

    def game_loop(self, dt: int):
        self.update_all_players_position(dt)
    
    def update_player_movement(self, client:'Client', key_states:'KeyStates', timestamp:int):
        player = self.players.get(client.id)
        if player:
            with self._lock:
                player.update_keystates(key_states)

    def send_position_updates(self, player:'Player'):
        for pid, other_player in self.players.items():
            if pid != player.client.id:
                other_player.client.send(ClientBoundPlayerPositionPacket(player.id, player.position))
        player.client.send(ClientBoundReconcilePositionPacket(time.time_ns(), player.position))

    def dt(self) -> float:
        return time.time() - self.last_update_time

    SPAWN_POSITION = None

    def update_all_players_position(self, dt: float = 0.05):
        from ursina import Vec3
        spawn = Vec3(0, 2, 0)
        for player in self.players.values():
            with self._lock:
                key_states = player.keys_states
            if key_states is not None:
                old_pos = copy.deepcopy(player.position)
                player.update_phy(dt, key_states)

                if player.position.y < 0:
                    player.position = spawn
                    print(f"World: respawn player {player.client.id} at {spawn}")
                    player.client.send(ClientBoundReconcilePositionPacket(time.time_ns(), spawn))
                    continue

                if player.position != old_pos:
                    print(f"World: updated player {player.client.id} position to {player.position}")
                    self.send_position_updates(player)

    def update_player_rotation(self, client:'Client', rotation:float, timestamp:int):
        player = self.players.get(client.id)
        if player:
            player.rotation_y = rotation

    def save(self):
        pass    

    def save_player_data(self):
        pass