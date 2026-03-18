from ursina import *

class FishingSpot(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'sphere'
        self.color = color.white
        # Range to interact for the fishing spot
        self.interaction_range = 5
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def interact(self):
        # Placeholder for entering combat
        self.color = color.red

    def update(self):
        pass