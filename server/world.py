
class World:

    def __init__(self):
        self.entities = {}
        self.next_entity_id = 0
        self.players = {}

    def add_entity(self, entity):
        entity_id = self.next_entity_id
        self.entities[entity_id] = entity
        self.next_entity_id += 1
        return entity_id