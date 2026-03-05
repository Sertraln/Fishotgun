from ursina import Entity,Vec3,lerp
from panda3d.bullet import BulletCapsuleShape, BulletRigidBodyNode, ZUp,BulletWorld
from panda3d.core import NodePath
from shared.parsedata.input import KeyStates
from shared.world import world_scene

class Physic(Entity):
    def __init__(self,parent:NodePath,position:Vec3 = Vec3(0,0,0), **kwargs):
        super().__init__(**kwargs)
        self.position = position
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
        body.setLinearDamping(0.0)

        self.body_np = parent.attachNewNode(body)
        self.body_np.setPos(self.position)
        bullet_world = world_scene.bullet_world
        bullet_world.attachRigidBody(body)
        self.body = body
        self.bullet_world = bullet_world

    def _update_pos(self, keys: KeyStates):
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
        #print("grounded : " ,self.grounded)
        if self.grounded and keys.is_pressed(KeyStates.JUMP):
            self.body.applyCentralImpulse(Vec3(0, 0, self.jump_force))
            self.grounded = False

    def ground_colision(self):
        """Set `self.grounded` if the body is touching a surface with an upward normal.

        Uses `contact_test` for efficiency, with a fallback to iterate persistent manifolds
        for compatibility with older API versions.
        """
        self.grounded = False

        # Prefer contact_test (returns BulletContactResult)
        res = self.bullet_world.contact_test(self.body)
        if res is not None:
            for i in range(res.get_num_contacts()):
                c = res.get_contact(i)
                mp = c.get_manifold_point()
                normal = mp.get_normal_world_on_b()
                if normal.z > 0.6:
                    self.grounded = True
                    return

        # Fallback: iterate persistent manifolds
        for manifold in self.bullet_world.get_manifolds():
            if manifold.get_node0() is self.body or manifold.get_node1() is self.body:
                for i in range(manifold.get_num_manifold_points()):
                    mp = manifold.get_manifold_point(i)
                    normal = mp.get_normal_world_on_b()
                    if normal.z > 0.6:
                        self.grounded = True
                        return

    def sync_visual(self):
        self.position = self.body_np.getPos()

    def update_phy(self, dt: float, key_states:KeyStates):
        if key_states.is_pressed(KeyStates.FORWARD):
            self.position += self.forward * dt * 5
        if key_states.is_pressed(KeyStates.BACKWARD):
            self.position -= self.forward * dt * 5
        if key_states.is_pressed(KeyStates.LEFT):
            self.position -= self.right * dt * 5
        if key_states.is_pressed(KeyStates.RIGHT):
            self.position += self.right * dt * 5
        if key_states.is_pressed(KeyStates.JUMP):
            self.position += Vec3(0, 5 * dt, 0)
        if key_states.is_pressed(KeyStates.SNEAK):
            self.position -= Vec3(0, 5 * dt, 0)
        return
        #todo physics
        self.bullet_world.doPhysics(dt)
        self.ground_colision()
        self._update_pos(key_states)
        self.sync_visual()