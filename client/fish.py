from ursina import *
from math import pi,atan2,sqrt,degrees,sin,cos
from random import randrange

import os
import sys
# Ensure project root is on sys.path so sibling packages like `shared` can be imported <--
_ROOT = os.path.dirname(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from shared.registry import Rarity
import client.data as data
from random import randrange, shuffle
from client import data

Y_OFFSET = -30
shot = Audio(
    "assets/musics/shot.wav",
    autoplay=False,
    volume=0.2
)

def get_angle(dx, dz):
    return (-degrees(atan2(dz, dx))) % 360

class FishType:
    ABONDANTS   = {'max_hp': 200,  'speed': 4, 'speedrot': 50, 'scale': 1.5}
    DISCRETS = {'max_hp': 500, 'speed': 4,   'speedrot': 80, 'scale': 1.0}
    INSAISISSABLES = {'max_hp': 1200, 'speed': 10, 'speedrot': 300, 'scale': 2.5}

RARITY_COLORS = {
    Rarity.ABONDANTS: color.white,
    Rarity.DISCRETS: color.blue,
    Rarity.INSAISISSABLES: color.gold
}

SHADOW_MAP = {
    "COMMUN": "assets/textures/fish_shadows/Communs.png",
    "CRUSTACE": "assets/textures/fish_shadows/Crustacés.png",
    "REQUIN": "assets/textures/fish_shadows/Requins.png",
    "MAGIQUE": "assets/textures/fish_shadows/Magiques.png"
}

class Fish(Entity):
    def __init__(self,fish_id, **kwargs):
        fish_type = kwargs.pop('fish_type', FishType.ABONDANTS)
        fish_category = kwargs.pop('category', 'COMMUN')
        super().__init__(**kwargs)
        self.fish_id = fish_id
        self.model = 'plane'
        self.texture = SHADOW_MAP.get(fish_category)
        self.model.setShaderOff()
        self.texture_scale = (1, 1)
        self.speedrot = fish_type['speedrot']
        self.scale = fish_type['scale']
        self.base_scale = self.scale
        self.speed = fish_type['speed']
        self.max_hp = fish_type['max_hp']
        self.hp = self.max_hp
        self.angle = 0
        self.collider = 'box'

        self._splash = Entity(
            parent=scene,
            model='quad',
            texture='assets/textures/water_splash.png',
            texture_scale=(1/4, 1/2),
            scale=2,
            rotation=(90, 0, 0),
            enabled=False
        )
        self._splash_frame = 0
        self._splash_timer = 0
        self._splash_playing = False

    def play_splash(self):
        self._splash_frame = 0
        self._splash_timer = 0
        self._splash_playing = True
        self._splash.enabled = True
        self._splash.position = self.position
        self._splash.rotation = (90, 0, 0)
        self._splash.texture_offset = (0, 0)

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

    def update(self):
        if not self._splash_playing:
            return
        self._splash_timer += time.dt
        if self._splash_timer > 0.15:
            self._splash_timer = 0
            self._splash_frame += 1
            if self._splash_frame >= 8:
                self._splash_playing = False
                self._splash.enabled = False
                self._splash.texture_offset = (0, 0)
                return
            col = self._splash_frame % 4
            row = self._splash_frame // 4
            self._splash.texture_offset = (col / 4, 1 - (row + 1) / 2)

_water_time_start = None

class FishingScene:
    BAR_X = 0.8
    BAR_BOTTOM = -0.3
    BAR_TOP = 0.3
    BAR_H = BAR_TOP - BAR_BOTTOM
    BAR_W = 0.03

    def __init__(self, on_end=None):
        self.on_end = on_end
        self.enabled = False
        self._stopping = False
        self.player_damage = 5
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
        self._cursor = None

    def start(self, server_fish_ids: list[int]):
        self.enabled = True
        self._stopping = False
        self._selected_fish : Fish = None
        self._fleeing = []
        self._pressure = 0.8
        self._saved_cam_pos = camera.position
        self._saved_cam_rot = camera.rotation

        self.player_damage = 5*data.player.level

        mouse.visible = False
        self._cursor = Entity(
            parent=camera.ui,
            model='quad',
            texture='assets/textures/crosshair.png',
            scale=0.05,
            z=-1
        )
        mouse.hotspot = (0.5, 0.5)

        camera.world_position = (0, Y_OFFSET, 0)
        camera.world_rotation = (90, 0, 0)
        data.player.disable()
        #camera.fov = 60

        self.parallax_container = Entity()

        y = Y_OFFSET - 10
        water = Entity(model='plane', texture='assets/textures/water.png', scale=50, position=(0, Y_OFFSET-13, 0), rotation=(0,0,0), texture_scale=(1,1))

        water.model.set_shader_input("texScale", 32.0)
        water_shader_path = application.asset_folder / 'assets' / 'shader' / 'water.fsh'
        water_shader_fragment = water_shader_path.read_text(encoding='utf-8')

        water_shader = Shader(name="water", vertex=data.default_vertex, fragment=water_shader_fragment)
        water_shader.compile()
        water.model.setShader(water_shader._shader)
        self._water_time_start = time.perf_counter()
        water.model.set_shader_input("iTime", 0.0)
        self._water_entity = water

        spawns = [(-4, y, -4), (4, y, -4), (-4, y, 4), (4, y, 4)]
        self._pairs = []
        
        from shared.registry import fish_list, Rarity

        for pos, f_id in zip(spawns, server_fish_ids):
            real_rarity = Rarity.ABONDANTS
            if 0 <= f_id < len(fish_list):
                real_rarity = fish_list[f_id].rarity

            if real_rarity == Rarity.INSAISISSABLES:
                ftype = FishType.INSAISISSABLES
            elif real_rarity == Rarity.DISCRETS:
                ftype = FishType.DISCRETS
            else:
                ftype = FishType.ABONDANTS

            fish = Fish(f_id,position=pos, rotation=(0,0,0), fish_type=ftype, category=fish_list[f_id].category, parent=self.parallax_container)

            point = Entity(model='sphere', position=(pos[0], y, pos[2]), alpha=0)
            fish.on_click = lambda f=fish: self._on_fish_click(f)
            self._pairs.append((fish, point))

        self._hp_bar_bg = Entity(parent=camera.ui, model='quad', color=color.dark_gray, scale=(0.4, 0.03), position=(-0.2, 0.42), origin=(-0.5, 0), enabled=False)
        self._hp_bar = Entity(parent=camera.ui, model='quad', color=color.lime, scale=(0.4, 0.03), position=(-0.2, 0.42), origin=(-0.5, 0), enabled=False, z=-0.01)
        self._hp_text = Text('', parent=camera.ui, position=(0, 0.46), origin=(0, 0), scale=1, enabled=False, font=data.fisho_font)

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
        self._label_top = Text('x2 DMG', parent=camera.ui, position=(self.BAR_X, self.BAR_TOP + 0.03), origin=(0, 0), scale=0.8, color=color.yellow, enabled=False,font=data.fisho_font)
        self._label_bot = Text('Fuite',  parent=camera.ui, position=(self.BAR_X, self.BAR_BOTTOM - 0.04), origin=(0, 0), scale=0.8, color=color.red, enabled=False,font=data.fisho_font)

        self._entities = [
            water,
            self._hp_bar_bg,
            self._hp_bar, self._hp_text,
            self._press_bar_bg, self._press_bar,
            self._label_top, self._label_bot
            ] + [e for pair in self._pairs for e in pair]

    def _on_fish_click(self, fish):
        # fish shot
        shot.play()
        fish.alpha_setter(0.2)
        fish.play_splash()

        fish.scale = fish.scale/1.75

        if self._stopping:
            return
        
        if self._selected_fish is None:
            self._select(fish)

        elif self._selected_fish == fish:
            self._deal_damage()

    def _spawn_damage_text(self, amount, position):
        damage_text = Text(
            text=f"-{amount}",
            position=position + Vec3(0, 2, 0),
            scale=2,
            color=color.red,
            billboard=True
        )

        damage_text.animate_position(damage_text.position + Vec3(0, 2, 0), duration=0.5, curve=curve.out_expo)
        damage_text.animate_scale(0, duration=0.5, delay=0.3, curve=curve.in_expo)
        
        destroy(damage_text, delay=0.8)

    def _deal_damage(self):
        fish   = self._selected_fish
        damage = self.player_damage * 2 if self._pressure >= 0.8 else self.player_damage
        self._spawn_damage_text(damage, fish.position)
        fish.hp -= damage
        self._update_hp_bar(fish)
        if fish.hp <= 0:
            try:
                from shared.registry import fish_list
                if hasattr(fish, 'fish_id') and 0 <= fish.fish_id < len(fish_list):
                    fish_data = fish_list[fish.fish_id]
                    self._caught_fish_name = fish_data.name
                            
                    from client.packet.serverbound import ServerBoundCatchFishPacket
                    if hasattr(data, 'network') and data.network:
                        data.network.send(ServerBoundCatchFishPacket(fish.fish_id))
                else:
                    self._caught_fish_name = fish_list[0].name
            except Exception as e:
                print(f"Erreur FishoDex local : {e}")
                self._caught_fish_name = "Poisson Inconnu"
            self.request_stop()
            
    def _select(self, chosen_fish:Fish):
        self._selected_fish = chosen_fish
        chosen_point = None
        for fish, point in self._pairs:
            if fish == chosen_fish:
                chosen_point = point
            else:
                destroy(point)
                self._entities.remove(point)
                self._fleeing.append(fish)
                fish.on_click = lambda f=fish: None
                dx  = fish.position[0] - chosen_fish.position[0]
                dz  = fish.position[2] - chosen_fish.position[2]
                mag = sqrt(dx**2 + dz**2)
                fish.flee_dir = (dx/mag, dz/mag) if mag > 0 else (1, 0)
        self._pairs = [(chosen_fish, chosen_point)]
        self._fish = chosen_fish
        self._point = chosen_point
        self._pressure = 1.0
        invoke(self._destroy_fleeing, delay=1.2)
        invoke(lambda: self._show_bars(chosen_fish), delay=1.2)

    def _destroy_fleeing(self):
        for fish in self._fleeing:
            if fish in self._entities:
                self._entities.remove(fish)
            destroy(fish._splash)
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
    
    def update_parallax(self):
        screen_ratio = 1.778
        limit_y = 0.5
        limit_x = 0.5 * screen_ratio

        target_x = max(min(mouse.x, limit_x), -limit_x)
        target_z = max(min(mouse.y, limit_y), -limit_y)
        
        self.parallax_container.x = lerp(self.parallax_container.x, -target_x * 2.0, time.dt * 10)
        self.parallax_container.z = lerp(self.parallax_container.z, -target_z * 2.0, time.dt * 10)
        
        if hasattr(self, '_water_entity'):
            self._water_entity.x = -target_x
            self._water_entity.z = -target_z

    def update(self):
        if not self.enabled or self._stopping:
            return
        if self._cursor:
            self._cursor.position = mouse.position
            
            self._cursor.rotation_z += 180 * time.dt
            
            target_scale = 0.065 if mouse.left else 0.05
            self._cursor.scale = lerp(self._cursor.scale, Vec2(target_scale, target_scale), time.dt * 15)

        self.update_parallax()
        if hasattr(self, '_water_entity') and self._water_entity:
            t = time.perf_counter() - self._water_time_start
            self._water_entity.model.set_shader_input("iTime", t % 4096.0)

        for fish in self._fleeing:
            dx, dz = fish.flee_dir
            fish.position = (
                fish.position[0] + dx*10*time.dt,
                fish.position[1],
                fish.position[2] + dz*10*time.dt)
            fish.set_rotation((-degrees(atan2(dz, dx))) % 360)

        for fish, point in self._pairs:

            if fish.alpha_getter() < 1:
                new_alpha = min(1.0, fish.alpha_getter() + 0.02 * time.dt * 60)

                min_scale = fish.base_scale * 0.7

                target_scale = fish.scale_x + 0.02 * time.dt * 60
                new_scale = max(min_scale, min(fish.base_scale, target_scale))

                fish.scale = new_scale
                fish.alpha_setter(new_alpha)

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
        self.enabled = False
        self._stopping = False

        camera.position = self._saved_cam_pos
        camera.rotation = self._saved_cam_rot
        data.player.enable()
        #camera.fov = self._saved_cam_fov

        for e in self._entities:   # ya que joël pour faire des vannes en com de son code mdr
            if hasattr(e, '_splash'):
                destroy(e._splash)
            destroy(e)
        self._entities = []
        self._pairs = []
        self._fish = None
        self._point = None
        self._fleeing = []
        self._pressure = 0.5
        self._hp_bar_bg = None
        self._hp_bar = None
        self._hp_text = None
        self._press_bar_bg = None
        self._press_bar = None
        self._label_top = None
        self._label_bot = None

        if self._cursor:
            destroy(self._cursor)
            self._cursor = None
        mouse.hotspot = (0, 0)
        mouse.visible = True

        bannertext = "Le poisson a fui... La prochaine fois sera la bonne!"
        text_color = color.white
        fish_id = None
        
        if hasattr(self, '_caught_fish_name') and self._caught_fish_name:
            from shared.registry import fish_list
            fish_data = fish_list[self._selected_fish.fish_id]
            
            bannertext = f"Tu as attrapé un {self._caught_fish_name} !!"
            text_color = RARITY_COLORS.get(fish_data.rarity, color.white)
            fish_id = self._selected_fish.fish_id
            self._caught_fish_name = None

        banner = Text(
            text=bannertext,
            position=(0, -0.4),
            origin=(0, 0),
            scale=1.5,
            color=text_color,
            parent=camera.ui,
            ignore_paused=True,
            font=data.fisho_font
        )
        
        def cleanup():
            banner.animate_scale(0, duration=0.5, curve=curve.in_out_expo)
            if 'fish_img' in locals():
                fish_img.animate_scale(0, duration=0.5, curve=curve.in_out_expo)
                if anim_sequence: anim_sequence.finish()
            
            destroy(banner, delay=0.5)
            if 'fish_img' in locals():
                destroy(fish_img, delay=0.5)

        if fish_id is not None:
            fish_img = Entity(
                parent=camera.ui,
                model='quad',
                texture=f"assets/textures/fish/{fish_list[fish_id].id}.png",
                scale=(0.3, 0.3),
                position=(0, -0.25),
                ignore_paused=True
            )
            anim_sequence = Sequence(
                Func(fish_img.animate, 'rotation_z', 15, duration=0.8, curve=curve.in_out_sine),
                Wait(0.8),
                Func(fish_img.animate, 'rotation_z', -15, duration=0.8, curve=curve.in_out_sine),
                Wait(0.8),
                loop=True
            )
            anim_sequence.start()
        invoke(cleanup, delay=2.5)
        data.hud.show()
        self._selected_fish = None