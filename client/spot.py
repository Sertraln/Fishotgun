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