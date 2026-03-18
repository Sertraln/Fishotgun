from client import data,menu,world
from ursina import Entity,color,Vec3,camera,TextField,dedent,Text,Texture,Shader,window
from shared.utils import get_local_ip

_name = "player"
SCROLL_MIN_Y = -0.2
SCROLL_MAX_Y = 0.3

class ServerButton(menu.FixedButton):
    def __init__(self, name, ip, port, parent,**kwargs):
        super().__init__(
            text=name,
            position=(0, SCROLL_MAX_Y-0.05-len(parent.children) * 0.12),
            scale=(0.5, 0.09),
            text_size=0.8,
            text_color=color.white,
            highlight_text_color=color.white,
            parent=parent,
            color=color.rgba32(50, 50, 60),
            highlight_color=color.rgba32(70, 70, 90),
        )
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._selected = False
        self.ip = ip
        self.port = port

    def on_click(self):
        if self.selected:
            self.selected = False
            self.connect()
        else:
            self.parent.unselected()
            self.selected = True

    def connect(self):
        global _name
        res = world.join_world(self.ip, self.port, _name)
        if res:
            print("Erreur : " + str(res))
            self.parent.show_error(res)
        else:
            menu.hide()

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        if value:
            self.color = color.rgba32(80, 120, 180)
        else:
            self.color = color.rgba32(50, 50, 60)


class AddServerMenu(menu.Menu):
    def __init__(self):
        super().__init__("join_menu")
        Text("Ajouter un serveur", parent=self, position=(0, 0.28, -0.1), origin=(0, 0), scale=1.4, color=color.white)
        self.texterr = Text("format : ip:port  (ex: localhost:5555)", parent=self, position=(0, 0.18, -0.1), origin=(0,0), scale=0.55, color=color.rgba32(180,180,180))
        self.te = menu.CustomTextField(max_lines=1, parent=self, scale=(0.45, 0.07), position=(0, 0.07, -0.1), text_size=1, naming_box="ip", bg_color=color.black,text_color=color.light_gray)
        self.te_name = menu.CustomTextField(max_lines=1, parent=self, scale=(0.45, 0.07), position=(0, -0.07, -0.1), text_size=1, naming_box="name", bg_color=color.black,text_color=color.light_gray)
        self.connect_but = menu.FixedButton(text='Confirmer', text_color=color.white, highlight_text_color=color.white, position=(0, -0.2), scale=(0.3, 0.08), text_size=0.9, parent=self, color=color.rgba32(60, 160, 80), highlight_color=color.rgba32(80, 190, 100))
        self.connect_but.on_click = self.rejoindre
        self.server_list_menu: 'ServerListMenu' = None

    def rejoindre(self):
        content = self.te.text
        lst = content.split(":")
        size = len(lst)
        if lst[0] == "":
            lst = [get_local_ip(), "5555"]
        if size == 1:
            lst.append("5555")
        if lst[0] == "localhost":
            lst[0] = get_local_ip()
        if self.server_list_menu is not None:
            self.server_list_menu.add_server_to_list(self.te_name.text, lst[0], int(lst[1]))
        else:
            print("Erreur : server_list_menu is None")
        menu.show(self.server_list_menu)


add_server = AddServerMenu()
menu.register_menu(add_server)


def build_server_list_shader(min_y, max_y):
    return f'''
#version 120

uniform vec4 cur_color;
uniform sampler2D p3d_Texture0;

varying vec2 uv;
    
void main() {{
    float y = (gl_FragCoord.y / {window.size.y}) - 0.5;
    if (y < {min_y} || y > {max_y}) discard;
    gl_FragColor = cur_color;
}}

'''

def build_server_list_shader_texture(min_y, max_y):
    return f'''
#version 120

uniform sampler2D p3d_Texture0;

varying vec2 uv;
    
void main() {{
    float y = (gl_FragCoord.y / {window.size.y}) - 0.5;
    if (y < {min_y} || y > {max_y}) discard;
    gl_FragColor = vec4(1.0)*texture2D(p3d_Texture0, uv)+vec4(1.0,1.0,1.0,0.0);
}}

'''

test_vertex = '''
#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;

attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;

varying vec2 uv;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uv = p3d_MultiTexCoord0;
}
'''



test = build_server_list_shader_texture(SCROLL_MIN_Y, SCROLL_MAX_Y)

server_list_shader = build_server_list_shader(SCROLL_MIN_Y, SCROLL_MAX_Y)



class ServerListMenu(menu.Menu):
    def __init__(self):
        super().__init__("server_list_menu")
        self.pause = True

        Text("Rejoindre un serveur", parent=self, position=(0, 0.38, -0.1), origin=(0, 0), scale=1.4, color=color.white)

        self.button_list = Entity(parent=self)
        self.button_list.position = Vec3(0, 0, -0.1)
        self.button_list.shader = Shader(name='test', vertex=test_vertex, fragment=server_list_shader)
        self.button_list.shader.compile()
        self.button_list.show_error = self.show_error
        self.button_list.unselected = self.unselected
        add_server.server_list_menu = self

        self.error_label = Text("", parent=self, position=(0, -0.28, -0.1), origin=(0, 0), scale=0.7, color=color.rgba32(220, 80, 80))

        self.back_but = menu.FixedButton(text='< Retour', text_color=color.white, highlight_text_color=color.white, position=(-0.28, -0.38), scale=(0.22, 0.07), text_size=0.8, parent=self, color=color.rgba32(70, 70, 80), highlight_color=color.rgba32(100, 100, 115))
        self.back_but.menu = None
        def back():
            self.unselected()
            menu.show(self.back_but.menu)
        self.back_but.on_click = back
        self.add_server_but = menu.FixedButton(text='+ Ajouter', text_color=color.white, highlight_text_color=color.white, position=(0.28, -0.38), scale=(0.22, 0.07), text_size=0.8, parent=self, color=color.rgba32(60, 130, 60), highlight_color=color.rgba32(80, 160, 80))
        self.add_server_but.on_click = lambda: menu.show(add_server)

    def add_server_to_list(self, name, ip, port):
        but = ServerButton(name, ip, port, self.button_list)
        but.shader = self.button_list.shader
        but.set_shader_input("cur_color", but.color)
        if but.text_entity:
            new_shad = Shader(name='test', vertex=test_vertex, fragment=test)
            new_shad.compile()
            but.text_entity.shader = new_shad

    def show_error(self, error):
        self.error_label.text = f"Erreur : {error}"

    def update(self):
        for but in self.button_list.children:
            but.set_shader_input("cur_color", but.color)

    def input(self, key):
        num_buttons = len(self.button_list.children)
        if key not in ('scroll up', 'scroll down'):
            return

        # No scrolling needed while all entries fit in the visible area.
        if num_buttons <= 4:
            self.button_list.y = 0
            return

        top_button_y = SCROLL_MAX_Y - 0.05
        last_button_y = top_button_y - (num_buttons - 1) * 0.12
        max_offset = max(0, SCROLL_MIN_Y - last_button_y + 0.05)

        if key == 'scroll down':
            self.button_list.y = min(max_offset, self.button_list.y + 0.03)
        elif key == 'scroll up':
            self.button_list.y = max(0, self.button_list.y - 0.03)

    def unselected(self):
        for but in self.button_list.children:
            but.selected = False


join_menu = ServerListMenu()
menu.register_menu(join_menu)


class MainMenu(menu.Menu):
    def __init__(self):
        super().__init__("main_menu")
        self.pause = True
        join_menu.back_but.on_click = lambda: menu.show(self)

        Text("FISHOTGUN", parent=self, position=(0, 0.3, -0.1), origin=(0, 0), scale=2.5, color=color.rgba32(80, 200, 220))

        self.te = menu.CustomTextField(
            max_lines=1, parent=self, scale=(0.38, 0.07),
            position=(0, 0.1, -0.1), text_size=1,
            naming_box="Nom du joueur :", bg_color=color.black
        )

        self.test = menu.FixedButton(
            text='Multijoueur',
            text_color=color.white,
            highlight_text_color=color.white,
            scale=(0.35, 0.08), text_size=0.9,
            position=(0, -0.05), parent=self,
            color=color.rgba32(60, 120, 180),
            highlight_color=color.rgba32(80, 150, 210),
        )
        self.test.on_click = self.switch(lambda: menu.show(join_menu))

        from ursina import application
        quit_btn = menu.FixedButton(
            parent=self, text='Quitter',
            text_color=color.white,
            highlight_text_color=color.white,
            scale=(0.35, 0.08), position=(0, -0.18),
            text_size=0.9, color=color.rgba32(160, 50, 50),
            highlight_color=color.rgba32(190, 70, 70),
        )
        quit_btn.on_click = application.quit

    from typing import Callable
    def switch(self, button: 'Callable'):
        def default_switch():
            global _name
            _name = self.te.text_field.text
            if _name == "":
                _name = "player"
            button()
        return default_switch


main_menu = MainMenu()
menu.show(main_menu)
menu.register_menu(main_menu)