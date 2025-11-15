from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

class ThirdPersonController(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera_offset = -5
        self.body = Entity(
            parent=self,
            model='cube',
            scale=(1,1.5,1),
            y=0.75)
        
        camera.z = self.camera_offset
        # Additional third person setup can go here

    def update(self):
        super().update()
        # Additional third person update can go here