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

        # Physique
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = Vec3(0, 0, 0)
        self.gravity = Vec3(0, -9.8, 0)

    def update(self):
        # Additional third person update can go here

        dt = time.dt

        self.acceleration = Vec3(0, 0, 0)
        self.acceleration += self.gravity

        if held_keys['shift']:
            self.body.color = color.red
            speed = 20
        else:
            self.body.color = color.blue
            speed = 10

        direction = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s'])

        if held_keys['space'] and self.y <= 4.01:
            self.velocity.y = 5

        direction = direction * speed

        if not held_keys['d'] or held_keys['a']:
            direction.x = direction.x / 3

        if not held_keys['w'] or held_keys['s']:
            direction.z = direction.z / 3

        self.acceleration += direction

        self.velocity.x -= self.velocity.x * dt
        self.velocity.y -= self.velocity.y * dt

        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

        if self.y < 0:
            self.y = 0
            self.velocity.y = 0

        