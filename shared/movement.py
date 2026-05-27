import math
from panda3d.bullet import BulletCapsuleShape, BulletRigidBodyNode, ZUp, BulletWorld
from panda3d.core import NodePath, Vec3 as PVec3
from shared.parsedata.input import KeyStates
from ursina import Vec3

VELOCITY_SMOOTH = 18.0

def ursina_to_panda(v: Vec3) -> PVec3:
    return PVec3(v.x, v.z, v.y)

def panda_to_ursina(v) -> Vec3:
    return Vec3(v.x, v.z, v.y)

class Physic:
    def __init__(self, parent: NodePath, bullet_world: BulletWorld, position: Vec3 = Vec3(0, 0, 0)):
        self.position = Vec3(position)
        self.rotation_y = 0.0

        self.height = 2.0
        self.radius = 0.5
        self.walk_speed = 12.0
        self.sprint_multiplier = 1.6
        self.jump_force = 15.0
        self.grounded = False

        shape = BulletCapsuleShape(self.radius, self.height - self.radius * 2, ZUp)
        body = BulletRigidBodyNode('Player')
        body.setMass(1.0)
        body.addShape(shape)
        body.setAngularFactor(PVec3(0, 0, 0))
        body.setFriction(0.0)
        body.setLinearDamping(0.0)

        ppos = ursina_to_panda(position)
        self.body_np = parent.attachNewNode(body)
        self.body_np.setPos(ppos)
        bullet_world.attachRigidBody(body)
        self.body = body
        self.bullet_world = bullet_world

    def set_position(self, position: Vec3):
        ppos = ursina_to_panda(position)
        self.body_np.setPos(ppos)
        self.body.setLinearVelocity(PVec3(0, 0, 0))
        self.body.clearForces()
        self.position = Vec3(position)

    def _update_pos(self, keys: KeyStates, dt: float):
        vel = self.body.getLinearVelocity()
        rad = math.radians(self.rotation_y)
        forward_x =  math.sin(rad)
        forward_y =  math.cos(rad)
        right_x   =  math.cos(rad)
        right_y   = -math.sin(rad)

        fwd_dir = Vec3(forward_x, forward_y, 0)
        rgt_dir = Vec3(right_x,   right_y,   0)

        move_dir = keys.get_direction(fwd_dir, rgt_dir)
        speed = self.walk_speed
        if keys.is_pressed(KeyStates.SPRINT):
            speed *= self.sprint_multiplier

        desired_x = move_dir.x * speed
        desired_y = move_dir.y * speed

        alpha = min(1.0, VELOCITY_SMOOTH * dt)
        new_vx = vel.x + (desired_x - vel.x) * alpha
        new_vy = vel.y + (desired_y - vel.y) * alpha

        self.body.setLinearVelocity(PVec3(new_vx, new_vy, vel.z))

        if self.grounded and keys.is_pressed(KeyStates.JUMP):
            self.body.setLinearVelocity(PVec3(new_vx, new_vy, 0))
            self.body.applyCentralImpulse(PVec3(0, 0, self.jump_force))
            self.grounded = False

    def _check_grounded(self):
        self.grounded = False
        result = self.bullet_world.contactTest(self.body)
        for i in range(result.getNumContacts()):
            contact = result.getContact(i)
            mp = contact.getManifoldPoint()
            normal = mp.getNormalWorldOnB()
            if normal.z > 0.6:
                self.grounded = True
                return
        for manifold in self.bullet_world.getManifolds():
            if manifold.getNode0() is self.body or manifold.getNode1() is self.body:
                for i in range(manifold.get_num_manifold_points()):
                    mp = manifold.getManifoldPoint(i)
                    normal = mp.getNormalWorldOnB()
                    if normal.z > 0.6:
                        self.grounded = True
                        return

    def _sync(self):
        pos = self.body_np.getPos()
        self.position = panda_to_ursina(pos)

    def update_phy(self, dt: float, key_states: KeyStates):
        self.bullet_world.doPhysics(dt)
        self._check_grounded()
        self._update_pos(key_states, dt)
        self._sync()