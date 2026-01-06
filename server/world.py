from typing import TYPE_CHECKING
from server import data
from server.packet.clientbound import *
import threading as th
from shared.movement import update_pos
import time

if TYPE_CHECKING:
    from server.player import Player
    from server.entity import Entity
    from shared.parsedata.input import KeyStates
    from server.client import Client

class World:
    def __init__(self):
        self.entities : dict[int,'Entity'] = {}
        self.tickrate = 20  # Ticks per second
        self.dt_per_tick = 1.0 / self.tickrate
        self.next_entity_id = 0
        self.players : dict[int,'Player'] = {}
        self.last_update_time = time.time()
        print("World: initialized")
        th.Thread(target=self._game_loop, daemon=True).start()

    def join_player(self, player:'Player') -> int:
        pid = player.client.id
        
        self.players[pid] = player
        player.client.send(ClientBoundPlayerListPacket(self.players.values()))
        print(f"World: player joined {pid}")
        data.server.broadcast(ClientBoundSpawnPlayerPacket(player),[player.client.id]) 
        return pid

    def left_player(self, pid:int):
        if pid in self.players:
            del self.players[pid]
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

    def game_loop(self,dt:int):
        self.update_all_players_position(dt)
    
    def update_player_movement(self, client:'Client', key_states:'KeyStates', timestamp:int):
        player = self.players.get(client.id)
        if player:
            player.update_keystates(key_states)

    def send_position_updates(self,player:'Player'):
        for pid, other_player in self.players.items():
            player.client.send(ClientBoundPlayerPositionPacket(pid,other_player.position))

    def dt(self) -> float:
        current_time = time.time()
        dt = current_time - self.last_update_time
        return dt

    def update_all_players_position(self,dt:float = 0.05):
        for player in self.players.values():
            if player.keys_states is not None:
                update_pos(player, dt, player.keys_states)
                self.send_position_updates(player)
                

    def save_player_data(self):
        pass