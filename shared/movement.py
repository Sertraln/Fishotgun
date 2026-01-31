from ursina import Entity, Vec3, render
from panda3d.bullet import BulletCapsuleShape, BulletRigidBodyNode, ZUp
from shared.parsedata.input import KeyStates

class Physic(Entity):
    def __init__(self, bullet_world):
        super().__init__()

        self.height = 2.0
        self.radius = 0.5

        self.walk_speed = 6.0
        self.sprint_multiplier = 1.6
        self.jump_force = 6.5

        self.grounded = False

        shape = BulletCapsuleShape(self.radius, self.height - self.radius * 2, ZUp)
        body = BulletRigidBodyNode('Player')
        body.setMass(1.0)
        body.addShape(shape)

        body.setAngularFactor(Vec3(0, 0, 0))
        body.setFriction(0.0)
        body.setLinearDamping(0.2)

        self.body_np = render.attachNewNode(body)
        self.body_np.setPos(self.position)

        bullet_world.attachRigidBody(body)
        self.body = body
        self.bullet_world = bullet_world

    def update_pos(self, dt: float, keys: KeyStates):
        vel = self.body.getLinearVelocity()

        move_dir = keys.get_direction(self.forward, self.right)
        speed = self.walk_speed

        if keys.is_pressed(KeyStates.SPRINT):
            speed *= self.sprint_multiplier

        desired_vel = Vec3(
            move_dir.x * speed,
            move_dir.y * speed,
            vel.z
        )

        current = self.body.getLinearVelocity()
        self.body.setLinearVelocity(Vec3(
            lerp(current.x, desired_vel.x, 0.2),
            lerp(current.y, desired_vel.y, 0.2),
            current.z
        ))

        if self.grounded and keys.is_pressed(KeyStates.JUMP):
            self.body.applyCentralImpulse(Vec3(0, 0, self.jump_force))
            self.grounded = False

    def ground_colision(self):
        self.grounded = False

        for contact in self.bullet_world.getContactManifolds():
            if contact.getNode1() == self.body or contact.getNode2() == self.body:
                for i in range(contact.getNumContacts()):
                    normal = contact.getContactPoint(i).getNormalWorldOnB()
                    if normal.z > 0.6:
                        self.grounded = True
                        return

    def sync_visual(self):
        self.position = self.body_np.getPos()


"""
def update():
    dt = time.dt

    bullet_world.doPhysics(dt)

    player.ground_colision()
    player.update_pos(dt, key_states)
    player.sync_visual()
"""