from ursina import Vec3,Entity,boxcast,Vec2,CapsuleCollider,raycast
from ursina.scene import Scene
from panda3d.core import NodePath

hitbox = Entity(parent=None, enabled=False)
hitbox.collider_setter(CapsuleCollider(hitbox, Vec3(0,0,0),2,0.5))

def det(a : Vec2, b : Vec2):
    """
    Calcule le déterminant d'une matrice 2x2:
    | a  b |
    | c  d |
    
    Retourne: a*d - b*c
    """
    return a.x * b.y - a.y * b.x


def intersection_droites(P1 : Vec2, v1:Vec2, P2:Vec2, v2:Vec2):
    """
    Calcule le point d'intersection de deux droites dans le plan 2D.
    
    Paramètres:
        P1: point de passage de la droite 1 [x, y]
        v1: vecteur directeur de la droite 1 [vx, vy]
        P2: point de passage de la droite 2 [x, y]
        v2: vecteur directeur de la droite 2 [vx, vy]
    
    Retourne:
        Le point d'intersection [x, y] ou None si les droites sont parallèles
    """
    d1 = det(v1, -v2)
    
    if abs(d1) < 1e-10:
        return None  # Droites parallèles ou confondues
    
    dv = P2-P1
    
    t = det(dv, -v2) / d1
    
    intersection_x = P1.x + t * v1.x
    intersection_y = P1.y + t * v1.y
    
    return Vec2(intersection_x, intersection_y)

def calculate_safe_movement(entity : Entity,mov:Vec3, mov_dir: Vec3,mov_len:float, colliders_to_test : NodePath) -> Vec3:
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

if __name__ == '__main__':
    print(intersection_droites(Vec2(0,11),Vec2(0,1),Vec2(2,10),Vec2(1,0)))