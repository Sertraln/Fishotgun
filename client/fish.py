from ursina import *
from math import pi,atan2,sqrt,degrees,sin,cos
from random import randrange, shuffle

Y_OFFSET = -30
shot = Audio(
    "assets/musics/shot.wav",
    autoplay=False,
    volume=0.8
)

def get_angle(dx, dz):
    return (-degrees(atan2(dz, dx))) % 360

class FishType:
    WEAK   = {'max_hp': 25,  'speed': 1, 'speedrot': 50, 'scale': 1.3}
    NORMAL = {'max_hp': 50, 'speed': 3,   'speedrot': 70, 'scale': 1.0}
    STRONG = {'max_hp': 100, 'speed': 5, 'speedrot': 90, 'scale': 0.7}

class Fish(Entity):
    def __init__(self, **kwargs):
        fish_type = kwargs.pop('fish_type', FishType.NORMAL)
        super().__init__(**kwargs)
        self.model = 'plane'
        self.texture = 'assets/textures/fish_shadow.png'
        self.texture_scale = (1, 1)
        self.speedrot = fish_type['speedrot']
        self.scale = fish_type['scale']
        self.speed = fish_type['speed']
        self.max_hp = fish_type['max_hp']
        self.hp = self.max_hp
        self.angle = 0
        self.collider = 'box'

    def set_rotation(self, angle: float):
        self.angle = angle % 360
        self.rotation = (0, angle, 0)

    def look_at(self, target_pos, catch_radius: float=1.2) -> bool:
        dx = target_pos[0] - self.position[0]
        dz = target_pos[2] - self.position[2]
        dist = sqrt(dx**2 + dz**2)
        if dist < catch_radius:
            return True
        p_angle = get_angle(dx, dz)
        self.angle = round(self.angle, 1)
        dif = self.angle - p_angle
        self.position = (
            self.position[0] + ((cos(-self.angle*pi/180) * self.speed) * time.dt),
            self.position[1],
            self.position[2] + ((sin(-self.angle*pi/180) * self.speed) * time.dt))
        speed = (self.speedrot + (abs(dif) / 1.5)) * time.dt
        if abs(dif) < speed and dist < catch_radius * 6:
            return True
        if dif < 0 and dif >= -180 or dif >= 180:
            self.set_rotation(self.angle + speed)
        else:
            self.set_rotation(self.angle - speed)
        return False


class FishingScene:
    BAR_X = 0.45
    BAR_BOTTOM = -0.3
    BAR_TOP = 0.3
    BAR_H = BAR_TOP - BAR_BOTTOM
    BAR_W = 0.03

    def __init__(self, on_end=None):
        self.on_end = on_end
        self.enabled = False
        self._stopping = False
        self.player_damage = 1
        self._entities = []
        self._pairs = []
        self._fish = None
        self._point = None
        self._selected_fish = None
        self._fleeing = []
        self._pressure = 0.5
        self._hp_bar_bg = None
        self._hp_bar = None
        self._hp_text = None
        self._press_bar_bg = None
        self._press_bar = None

    def start(self):
        self.enabled = True
        self._stopping = False
        self._selected_fish = None
        self._fleeing = []
        self._pressure = 0.8
        self._saved_cam_pos = camera.position
        self._saved_cam_rot = camera.rotation
        self._saved_cam_fov = camera.fov

        camera.position = (0, Y_OFFSET, 0)
        camera.rotation = (90, 0, 0)
        camera.fov      = 60

        y = Y_OFFSET - 19
        water = Entity(model='plane', texture='assets/textures/water.png', scale=30, position=(0, Y_OFFSET-20, 0), rotation=(0,0,0),texture_scale=(5,5))

        types = [FishType.WEAK, FishType.NORMAL, FishType.NORMAL, FishType.STRONG]
        shuffle(types)
        spawns = [(-4, y, -4), (4, y, -4), (-4, y, 4), (4, y, 4)]
        self._pairs = []
        for pos, ftype in zip(spawns, types):
            fish  = Fish(position=pos, rotation=(0,0,0), fish_type=ftype)
            point = Entity(model='sphere', position=(pos[0], y, pos[2]), alpha=0)
            fish.on_click = lambda f=fish: self._on_fish_click(f)
            self._pairs.append((fish, point))

        # BARRE HP DU POISCAILLE
        self._hp_bar_bg = Entity(parent=camera.ui, model='quad', color=color.dark_gray, scale=(0.4, 0.03), position=(-0.2, 0.42), origin=(-0.5, 0), enabled=False)
        self._hp_bar = Entity(parent=camera.ui, model='quad', color=color.lime, scale=(0.4, 0.03), position=(-0.2, 0.42), origin=(-0.5, 0), enabled=False, z=-0.01)
        self._hp_text = Text('', parent=camera.ui, position=(0, 0.46), origin=(0, 0), scale=1, enabled=False)

        # BARRE "PRESSION" DU JOUEUR
        self._press_bar_bg = Entity(
            parent=camera.ui, model='quad', color=color.dark_gray,
            scale=(self.BAR_W, self.BAR_H),
            position=(self.BAR_X, self.BAR_BOTTOM),
            origin=(0, -0.5), enabled=False)
        self._press_bar = Entity(
            parent=camera.ui, model='quad', color=color.cyan,
            scale=(self.BAR_W, self.BAR_H * self._pressure),
            position=(self.BAR_X, self.BAR_BOTTOM),
            origin=(0, -0.5), enabled=False, z=-0.01)
        self._label_top = Text('x2 DMG', parent=camera.ui, position=(self.BAR_X, self.BAR_TOP + 0.03), origin=(0, 0), scale=0.8, color=color.yellow, enabled=False)
        self._label_bot = Text('Fuite',  parent=camera.ui, position=(self.BAR_X, self.BAR_BOTTOM - 0.04), origin=(0, 0), scale=0.8, color=color.red, enabled=False)

        self._entities = [
            water,
            self._hp_bar_bg,
            self._hp_bar, self._hp_text,
            self._press_bar_bg, self._press_bar,
            self._label_top, self._label_bot
            ] + [e for pair in self._pairs for e in pair]

    def _on_fish_click(self, fish):
        shot.play()
        if self._stopping:
            return
        if self._selected_fish is None:
            # fish shot
            # fish.alpha_setter(0.2)
            self._select(fish)
        elif self._selected_fish == fish:
            # fish shot
            # fish.alpha_setter(0.2)
            # print("heyy !! you shot me !")
            self._deal_damage()

    def _get_shot(self):
        fish   = self._selected_fish
        fish

    def _deal_damage(self):
        fish   = self._selected_fish
        damage = self.player_damage * 2 if self._pressure >= 0.8 else self.player_damage
        fish.hp -= damage
        self._update_hp_bar(fish)
        if fish.hp <= 0:
            self.request_stop()
        

    def _select(self, chosen_fish):
        self._selected_fish = chosen_fish
        chosen_point = None
        for fish, point in self._pairs:
            if fish == chosen_fish:
                chosen_point = point
            else:
                destroy(point)
                self._entities.remove(point)
                self._fleeing.append(fish)
                dx  = fish.position[0] - chosen_fish.position[0]
                dz  = fish.position[2] - chosen_fish.position[2]
                mag = sqrt(dx**2 + dz**2)
                fish.flee_dir = (dx/mag, dz/mag) if mag > 0 else (1, 0)
        self._pairs = [(chosen_fish, chosen_point)]
        self._fish = chosen_fish
        self._point = chosen_point
        self._pressure = 0.5
        invoke(self._destroy_fleeing, delay=1.2)
        invoke(lambda: self._show_bars(chosen_fish), delay=1.2)

    def _destroy_fleeing(self):
        for fish in self._fleeing:
            if fish in self._entities:
                self._entities.remove(fish)
            destroy(fish)
        self._fleeing = []

    def _show_bars(self, fish):
        for e in [self._hp_bar_bg, self._hp_bar, self._hp_text, self._press_bar_bg, self._press_bar, self._label_top, self._label_bot]:
            e.enabled = True
        self._update_hp_bar(fish)
        self._update_pressure_bar()

    def _update_hp_bar(self, fish):
        ratio = max(0, fish.hp / fish.max_hp)
        self._hp_bar.scale_x = 0.4 * ratio
        self._hp_bar.color = color.green if ratio > 0.5 else (color.orange if ratio > 0.25 else color.red)
        self._hp_text.text = f'{max(0, fish.hp)} / {fish.max_hp}'

    def _update_pressure_bar(self):
        self._press_bar.scale_y = self.BAR_H * self._pressure
        self._press_bar.color = color.green if self._pressure >= 0.8 else (color.yellow if self._pressure > 0.55 else (color.orange if self._pressure > 0.3 else color.red))

    def request_stop(self):
        if not self.enabled or self._stopping:
            return
        self._stopping = True
        if self.on_end:
            self.on_end('caught')

    def update(self):
        if not self.enabled or self._stopping:
            return
        for fish in self._fleeing:
            dx, dz = fish.flee_dir
            fish.position = (
                fish.position[0] + dx*10*time.dt,
                fish.position[1],
                fish.position[2] + dz*10*time.dt)
            fish.set_rotation((-degrees(atan2(dz, dx))) % 360)
            # if (fish.alpha_getter() < 1) :
            #     fish.alpha_setter(fish.alpha_getter() + 0.1)
        for fish, point in self._pairs:
            # if (fish.alpha_getter() < 1) :
            #         fish.alpha_setter(fish.alpha_getter() + 0.1)

            if self._selected_fish and fish == self._selected_fish:
                if mouse.world_point:
                    mdx = mouse.world_point[0] - fish.position[0]
                    mdz = mouse.world_point[2] - fish.position[2]
                    mouse_dist = sqrt(mdx**2 + mdz**2)
                    #fish.speed = max(1, speed*3-mouse_dist*6) # Le poisson nage plus vite quand la souris est proche
                    on_fish = mouse_dist < 1.5
                else:
                    on_fish = False
                self._pressure += (0.4 if on_fish else -0.6) * time.dt
                self._pressure  = max(0.0, min(1.0, self._pressure))
                self._update_pressure_bar()
                if self._pressure <= 0.0:
                    self.request_stop()
                    return
                
                

            if fish and point:
                if fish.look_at(point.position):
                    point.position = (randrange(-11, 11), Y_OFFSET-19, randrange(-6, 6))

    def stop(self):
        if not self.enabled:
            return
        self.enabled   = False
        self._stopping = False
        camera.position = self._saved_cam_pos
        camera.rotation = self._saved_cam_rot
        camera.fov      = self._saved_cam_fov
        for e in self._entities: # On reset tout mdr
            destroy(e)
        self._entities = []
        self._pairs = []
        self._fish = None
        self._point = None
        self._selected_fish = None
        self._fleeing = []
        self._pressure = 0.5
        self._hp_bar_bg = None
        self._hp_bar = None
        self._hp_text = None
        self._press_bar_bg = None
        self._press_bar = None
        self._label_top = None
        self._label_bot = None