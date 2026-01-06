from ursina import Vec3,Entity,boxcast,Vec2,CapsuleCollider,raycast
from ursina.scene import Scene
from panda3d.core import NodePath
from shared.parsedata.input import KeyStates

from ursina import Vec3,Entity
from panda3d.core import NodePath

class Physic(Entity):
    def __init__(self):
        super().__init__()
        self.height: float = 2
        self.radius: float = 0.5
        self.center: Vec3 = Vec3(self.position.x, self.position.y + self.height / 2, self.position.z)
        self.acceleration: Vec3 = Vec3(0, 0, 0)
        self.vitesse: Vec3 = Vec3(0, 0, 0)
        self.jump_height: float = 0.3
        self.gravity: float = -0.6
        self.air_time: float = 0
        self.grounded = False
        self.ignore_list = [self]
        self.speed:float = 1

    def _calculate_speed(self,key_strokes:KeyStates):
        if key_strokes.is_pressed(KeyStates.SPRINT):
            return 1.6
        else:
            return 1.0

hitbox = Entity(parent=None, enabled=False)
hitbox.collider_setter(CapsuleCollider(hitbox, Vec3(0,0,0),2,0.5))

def calculate_safe_movement(entity : Physic ,mov:Vec3, mov_dir: Vec3,mov_len:float, colliders_to_test : NodePath) -> Vec3:
    """
    Calcule le mouvement final en gérant les collisions et le glissement.
    Ne gère que les axes X et Z (mouvement horizontal).
    
    Args:
        entity: L'objet qui se déplace (doit avoir .position et .intersects())
        desired_movement: Vec3 du mouvement souhaité (seuls x et z sont traités)
        colliders_to_test: Liste des objets avec lesquels tester les collisions
    
    Returns:
        Vec3: Le mouvement final à appliquer (peut être différent du mouvement souhaité)
    """
    if mov_len < 0.001:
        return Vec3(0, mov.y, 0)
    height = hitbox._collider.height
    radius = hitbox._collider.radius
    origin = entity.position + Vec3(0, entity.height / 2 + 0.5, 0)
    size = (radius,height)
    hitresult = boxcast(origin,Vec3(mov.x,0,mov.z),mov_len,size,colliders_to_test,debug=True)

    if not hitresult.hit:
        return mov
    
    # Collision detected, calculate sliding movement
    normal :Vec3 = hitresult.world_normal
    mov_dir_2d = Vec2(mov_dir.x, mov_dir.z)
    if mov_dir_2d.length() < 0.01:  # Pas de glissement si pas de mouvement intentionnel
        return mov
    
    # Projeter le mouvement sur le plan tangent (glissement)
    mov_2d = Vec2(mov.x, mov.z)
    normal_2d = Vec2(normal.x, normal.z).normalized()
    dot = mov_2d.dot(normal_2d)
    slide_2d = mov_2d - normal_2d * dot
    slide_vector = Vec3(slide_2d.x, mov.y, slide_2d.y)
    
    # Vérifier si le mouvement glissé est possible
    slide_len = slide_2d.length()
    if slide_len > 0:
        hitresult_slide = boxcast(origin, Vec3(slide_2d.x, 0, slide_2d.y), slide_len, size, colliders_to_test, debug=True)
        if hitresult_slide.hit:
            # Limiter le mouvement glissé à la distance de collision
            slide_len = hitresult_slide.distance
            slide_2d = slide_2d.normalized() * slide_len
    slide_vector = Vec3(slide_2d.x, mov.y, slide_2d.y)
    return slide_vector

from shared.world import world_scene as colliders_to_test

def update_pos(player:Physic,dt:float, key_strokes:KeyStates):
    player.acceleration = Vec3(0, 0, 0)
    player.acceleration.y += player.gravity * dt
    if player.grounded:
        player.air_time = 0
        if key_strokes.is_pressed(KeyStates.JUMP):
            player.acceleration.y =player.jump_height
            player.grounded = False

    player.speed = player._calculate_speed(key_strokes)
    air_reducion = 0.3 if not player.grounded else 1
    mov_dir = key_strokes.get_direction(player.forward,player.right)
    direction : Vec3 = mov_dir * player.speed * air_reducion * dt * 1.5
    player.acceleration += direction
    player.vitesse = player.vitesse + player.acceleration  

    friction_factor = pow(10000, dt)
    air_friction_factor = pow(6, dt)
    if not player.grounded:
        friction_factor = air_friction_factor
        player.vitesse.y *= 0.98  # Simulate air resistance on vertical movement
    player.vitesse.x /= friction_factor
    player.vitesse.z /= friction_factor
    if not player.grounded:
        player.air_time += dt
    player.vitesse = calculate_safe_movement(player,player.vitesse,mov_dir,player.vitesse.xz_getter().length(),colliders_to_test)
    ground_colision(player,colliders_to_test)
    player.position += player.vitesse
    

def ground_colision(player: Physic,traverse_target:NodePath):
    y_speed = player.vitesse.y
    ground_ray = raycast(player.position+Vec3(0,player.height-0.2,0), Vec3(0,-1,0),
            distance=player.height-0.2-y_speed, traverse_target=traverse_target,
            ignore=player.ignore_list, debug=False)
    head_ray = raycast(player.position+Vec3(0,0.2,0), Vec3(0,1,0),
            distance=player.height-0.2+y_speed, traverse_target=traverse_target,
            ignore=player.ignore_list, debug=False)
    if ground_ray.hit and player.vitesse.y <= 0:
        player.grounded = True
        player.y = ground_ray.world_point.y
        player.vitesse.y = 0
    elif head_ray.hit and player.vitesse.y > 0:
        player.vitesse.y = 0
        player.position.y = head_ray.world_point.y - player.height -0.1
    else:
        player.grounded = False