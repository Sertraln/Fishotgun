from ursina import *

class FishingSpot(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'sphere'
        self.color = color.white
        self.interaction_range = 5
        self._scene = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    def set_scene(self, scene):
        self._scene = scene

    def interact(self):
        if self._scene:
            self._scene.start()

    def on_fishing_end(self, result):
        print(f"Fishing ended: {result}")

    def update(self):
        pass


class BusSpot(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'sphere'
        self.color = color.white
        self.interaction_range = 5
        for key, value in kwargs.items():
            setattr(self, key, value)

    def interact(self):
        from client import data
        from client.packet.serverbound import ServerBoundTeleportPacket
        if data.player:
            pos = Vec3(10, 0, -40) # <- changer ici par l emplacement voulu pour le shop les guys
            data.player.position = pos
            data.player.physic.position = pos
            data.player._queue_pos.clear()
            data.network.send(ServerBoundTeleportPacket(pos))