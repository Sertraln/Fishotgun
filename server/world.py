from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server.player import Player
    from server.entity import Entity

class World:

    def __init__(self):
        self.entities : dict[int,'Entity'] = {}
        self.next_entity_id = 0
        self.players : dict[int,'Player'] = {}

    def join_player(self, player:'Player') -> int:
        pid = player.client.id
        self.players[pid] = player
        print(f"World: player joined {pid}")
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

    def add_entity(self, entity):
        entity_id = self.next_entity_id
        self.entities[entity_id] = entity
        self.next_entity_id += 1
        return entity_id