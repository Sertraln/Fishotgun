from typing import TYPE_CHECKING
from server import data
from server.packet.clientbound import *
import threading as th
import time
from shared import world
from ursina import scene
import copy

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
        world.init_world(scene)
        print("World: initialized")
        th.Thread(target=self._game_loop, daemon=True).start()

    @property
    def world_scene(self):
        return world.world_scene

    def join_player(self, player:'Player') -> int:
        player.client.send(ClientBoundInitPlayerPacket(player))
        player.client.send(ClientBoundPlayerListPacket(list(self.players.values())))
        pid = player.client.id
        self.players[pid] = player
        print(f"World: player joined {pid} - {player.player_name}")
        data.server.broadcast(ClientBoundSpawnPlayerPacket(player),[player.client.id]) 
        return pid

    def left_player(self, pid:int):
        print(f"DEBUG: Tentative de déconnexion pour le joueur {pid}")
        
        if pid in self.players:
            player = self.players.pop(pid)
            
            if player is not None:
                print(f"DEBUG: Appel de la méthode save() pour le joueur {player.unique_id}")
                player.save()
            else:
                print(f"DEBUG: Erreur, le joueur {pid} était None dans le dictionnaire")
                
            data.server.broadcast(ClientBoundPlayerLeavePacket(pid),[pid])
            print(f"World: player left {pid}")
        else:
            print(f"DEBUG: Le joueur {pid} n'était pas dans self.players (déjà déconnecté ?)")

    def stop(self):
        print("World: Arret du monde, sauvegarde de tous les joueurs connectes...")
        for pid in list(self.players.keys()):
            self.left_player(pid)
        self.players.clear()

    def save(self):
        print("World: Sauvegarde generale declenchee...")
        for player in self.players.values():
            try:
                player.save()
            except Exception as e:
                print(f"World: Echec de sauvegarde de secours pour {player.client.id} : {e}")

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
            if pid != player.client.id:
                other_player.client.send(ClientBoundPlayerPositionPacket(player.id,player.position))
        player.client.send(ClientBoundReconcilePositionPacket(time.time_ns(),player.position))

    def dt(self) -> float:
        current_time = time.time()
        dt = current_time - self.last_update_time
        return dt

    def update_all_players_position(self,dt:float = 0.05):
        for player in self.players.values():
            if player.keys_states is not None:
                old_pos = copy.deepcopy(player.position)
                player.update_phy(dt, player.keys_states)
                if player.position != old_pos:  # Only send updates if player has moved significantly
                    print(f"World: updated player {player.client.id} position to {player.position}")
                    self.send_position_updates(player)

    def update_player_rotation(self, client:'Client', rotation:float, timestamp:int):
        player = self.players.get(client.id)
        if player:
            player.rotation_z = rotation