from ursina import Entity,Vec3,lerp
from panda3d.bullet import BulletCapsuleShape, BulletRigidBodyNode, YUp,BulletWorld
from panda3d.core import NodePath
from shared.parsedata.input import KeyStates
from shared.world import world_scene

class Physic(Entity):
    def __init__(self,parent:NodePath,position:Vec3 = Vec3(0,0,0), **kwargs):
        if parent is None:
            from panda3d.core import NodePath
            parent = render if 'render' in globals() else NodePath("ServerRoot")
        super().__init__(**kwargs)
        self.height = 2.0
        self.radius = 0.5
        self.walk_speed = 6.0
        self.sprint_multiplier = 1.6
        self.jump_force = 10.0
        self.rotation_y = 0
        self.grounded = False

        shape = BulletCapsuleShape(self.radius, self.height - self.radius * 2, YUp)
        body = BulletRigidBodyNode('Player')
        body.setMass(1.0)
        body.addShape(shape)
        body.setAngularFactor(Vec3(0, 0, 0))
        body.setFriction(0.0)
        body.setLinearDamping(0.1)
        self.body = body

        self.body.setDeactivationEnabled(False)
        self.body_np = parent.attachNewNode(body)
        self.body_np.setPos(position)
        

        self.bullet_world = world_scene.bullet_world
        self.bullet_world.attachRigidBody(self.body)




    def update_phy(self, dt: float, keys: KeyStates):
        self.body_np.setH(self.rotation_y)

        self._update_pos(keys)

        self.ground_colision()

        self.sync_visual()






    def _update_pos(self, keys: KeyStates):
        vel = self.body.getLinearVelocity()
        move_dir = keys.get_direction(self.forward, self.right)

        if move_dir.length() > 0:
            print(f"Mouvement détecté ! Direction: {move_dir}")

        speed = self.walk_speed
        if keys.is_pressed(KeyStates.SPRINT):
            speed *= self.sprint_multiplier

        desired_vel = Vec3(
            move_dir.x * speed,
            vel.y,
            move_dir.z * speed
        )

        self.body.setLinearVelocity(Vec3(
            lerp(vel.x, desired_vel.x, 0.25),
            vel.y,
            lerp(vel.z, desired_vel.z, 0.25),
        ))

        if self.grounded and keys.is_pressed(KeyStates.JUMP):
            self.body.applyCentralImpulse(Vec3(0, self.jump_force, 0))
            self.grounded = False




    def ground_colision(self):
        self.grounded = False

        res = self.bullet_world.contact_test(self.body)

        if res:
            for i in range(res.get_num_contacts()):
                c = res.get_contact(i)
                mp = c.get_manifold_point()
                normal = mp.get_normal_world_on_b()
                if normal.y > 0.6:
                    self.grounded = True
                    return




    def sync_visual(self):
        self.position = self.body_np.getPos()




