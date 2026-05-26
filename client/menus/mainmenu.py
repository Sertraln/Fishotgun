from client import data,menu,world
from ursina import Entity,color,Vec3,camera,TextField,dedent,Text,Texture,Shader,window,invoke
from shared.utils import get_local_ip
import traceback

_name = "player"
SCROLL_MIN_Y_SHADER = -0.2
SCROLL_MAX_Y_SHADER = 1.4
SCROLL_MIN_Y = -0.2
SCROLL_MAX_Y = 0.25


class ServerButton(menu.FixedButton):
    lock_click = False

    def __init__(self, name, ip, port, parent,**kwargs):
        super().__init__(
            text=name,
            position=(0, SCROLL_MAX_Y-0.05-len(parent.children) * 0.06),
            scale=(0.5, 0.09),
            parent=parent,
        )
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._selected = False
        self.ip = ip
        self.port = port
        self.text_name = name
        self.enable()

    def on_click(self):
        if ServerButton.lock_click:
            return
        if self.selected:
            self.selected = False
            self.connect()
        else:
            self.parent.unselected()
            self.selected = True
            self.parent.parent.delete_button.show()
            self.parent.selected_button = self

    def connect(self):
        global _name
        ServerButton.lock_click = True
        try:
            world.join_world(self.ip, self.port, _name)
        except Exception as exc:
            print("Erreur : " + str(exc))
            traceback.print_exc()
            self.parent.show_error(exc)
            return
        else:
            menu.hide()
        ServerButton.lock_click = False

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
        self.text = Text("Ajouter un serveur", parent=self, position=(0, 0.28, -0.1), origin=(0, 0), scale=1.4, color=color.black,font=data.fisho_font)
        self.texterr = Text("format : ip:port  (ex: localhost:5555)", parent=self, position=(0, 0.18, -0.1), origin=(0,0), scale=0.55, color=color.black,font=data.fisho_font,text_size=0.9)
        self.te = menu.CustomTextField(max_lines=1, parent=self, scale=(0.45, 0.07), position=(0, 0.07, -0.1), text_size=1, naming_box="ip", bg_color=color.black,text_color=color.black)
        self.te_name = menu.CustomTextField(max_lines=1, parent=self, scale=(0.45, 0.07), position=(0, -0.07, -0.1), text_size=1, naming_box="name", bg_color=color.black,text_color=color.black)
        self.connect_but = menu.FixedButton(text='Confirmer', text_color=color.white, highlight_text_color=color.white, position=(0.1, -0.2), scale=(0.3, 0.08), text_size=0.9, parent=self, color=color.rgba32(60, 160, 80), highlight_color=color.rgba32(80, 190, 100))
        self.connect_but.on_click = self.add_server
        self.server_list_menu: 'ServerListMenu' = None
        self.back_button = menu.FixedButton(text="< Retour", position=(-0.1, -0.2), scale=(0.3, 0.08), text_size=0.9, parent=self, color=color.rgba32(70, 70, 80), highlight_color=color.rgba32(100, 100, 115))
        def back():
            self.hide()
            self.clear()
            menu.rotate_page_and_run([ lambda: menu.show(self.server_list_menu), lambda: self.show()],-1)
        self.back_button.on_click = back

    def clear(self):
        self.te.text_field.text = ""
        self.te.text_field.render()
        self.te_name.text_field.text = ""
        self.te_name.text_field.render()

    def add_server(self):
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
        self.clear()
        menu.hide()
        menu.rotate_page_and_run([lambda: menu.show(self.server_list_menu),lambda: self.show()],-1)


add_server = AddServerMenu()
menu.register_menu(add_server)


def build_server_list_shader(min_y, max_y):
    return f'''
#version 120

uniform vec4 cur_color;
uniform float window_height;
uniform sampler2D p3d_Texture0;

varying vec2 uv;
    
void main() {{
    float y = (gl_FragCoord.y / window_height) - 0.5;
    if (y < {min_y} || y > {max_y}) discard;
    gl_FragColor = cur_color;
}}

'''

def build_server_list_shader_texture(min_y, max_y):
    return f'''
#version 120

uniform float window_height;
uniform sampler2D p3d_Texture0;
uniform vec3 color;

varying vec2 uv;
    
void main() {{
    float y = (gl_FragCoord.y / window_height) - 0.5;
    if (y < {min_y} || y > {max_y}) discard;
    gl_FragColor = vec4(1.0)*texture2D(p3d_Texture0, uv)+vec4(color,0.0);
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
        Text("Rejoindre un serveur", parent=self, position=(0, 0.3, -0.1), origin=(0, 0),
              scale=1.4, color=color.black,font=data.fisho_font)
        self.button_list = Entity(parent=self,name="button_list")
        self.button_list.shader = Shader(name='test', vertex=test_vertex, fragment=server_list_shader)
        self.button_list.shader.compile()
        self.button_list.show_error = self.show_error
        self.button_list.unselected = self.unselected
        add_server.server_list_menu = self
        self.button_list.position=Vec3(0.0,0,0.0)
        self.error_label = Text("", parent=self, position=(0, -0.28, -0.1), origin=(0, 0), scale=0.7, color=color.rgba32(220, 80, 80))
        self.back_but = menu.FixedButton(text="< Retour",
                        position=(-0.19, -0.3),scale=(0.22, 0.07),
                        text_size=1.2, parent=self, color=color.rgba32(70, 70, 80),
                        highlight_color=color.rgba32(100, 100, 115))
        self.back_but.menu = None
        def back():
            self.unselected()
            self.hide()
            menu.rotate_page_and_run([ lambda: menu.show(self.back_but.menu), lambda: self.show()],-1)
        self.back_but.on_click = back
        self.add_server_but = menu.FixedButton(text='+ Ajouter',
                        position=(0.2, -0.3), scale=(0.22, 0.07), text_size=1.2, parent=self,
                        color=color.rgba32(60, 130, 60), highlight_color=color.rgba32(80, 160, 80))
        def add_server_func():
             self.hide()
             menu.rotate_page_and_run([ lambda: menu.show(add_server), lambda: self.show()],1)
        self.add_server_but.on_click = add_server_func
        self.delete_button = menu.FixedButton(text='Supprimer',
                        position=(0, -0.3), scale=(0.22, 0.07), text_size=1.2, parent=self,
                        color=color.rgba32(130, 60, 60), highlight_color=color.rgba32(160, 80, 80))
        self.delete_button.hide()
        self.button_list.selected_button = None
        self.delete_button.on_click = lambda: self.remove_serveur_button(self.button_list.selected_button)

    def add_server_to_list(self, name, ip, port):
        but = ServerButton(name, ip, port, self.button_list, color=color.black, text_size=1.2)
        if but.text_entity:
            new_shad = Shader(name='text', vertex=test_vertex, fragment=test)
            new_shad.compile()
            but.text_entity.shader = new_shad
            but.text_entity.set_shader_input("cur_color", but.color)

    def show_error(self, error):
        self.error_label.text = f"Erreur : {error}"

    def update(self):
        for but in self.button_list.children:
            but.set_shader_input("cur_color", but.color)
            but.set_shader_input("window_height", window.size[1])
            if but.model:
                but.model.set_shader_input("cur_color", but.color)
                but.model.set_shader_input("window_height", window.size[1])
            if but.text_entity:
                but.text_entity.set_shader_input("window_height", window.size[1])

    def input(self, key):
        num_buttons = len(self.button_list.children)
        if key not in ('scroll up', 'scroll down'):
            return
        # No scrolling needed while all entries fit in the visible area.
        if num_buttons <= 7:
            self.button_list.y = 0
            return
        top_button_y = SCROLL_MAX_Y - 0.05
        last_button_y = top_button_y - (num_buttons - 1) * 0.12
        max_offset = max(0, SCROLL_MIN_Y - last_button_y + 0.05)

        if key == 'scroll down':
            self.button_list.y = min(max_offset, self.button_list.y + 0.015)
        elif key == 'scroll up':
            self.button_list.y = max(0, self.button_list.y - 0.015)

    def unselected(self):
        for but in self.button_list.children:
            but.selected = False
        self.delete_button.hide()
        self.button_list.selected_button = None

    def remove_serveur_button(self, button:Entity):
        button.parent = None
        button.disable()
        button.remove_node()
        for i,but in enumerate(self.button_list.children):
            but.position = Vec3(0, SCROLL_MAX_Y-0.05-i*0.06, -0.1)
        self.unselected()

    def save(self) -> bytes:
        res = b''
        res += len(self.button_list.children).to_bytes(2, 'big')
        for but in self.button_list.children:
            name_bytes = but.text_name.encode('utf-8')
            ip_bytes = but.ip.encode('utf-8')
            port_bytes = but.port.to_bytes(2, 'big')
            res += len(name_bytes).to_bytes(2, 'big') + name_bytes
            res += len(ip_bytes).to_bytes(2, 'big') + ip_bytes
            res += port_bytes
        return res

    def load(self,bytes_data: bytes) -> None:
        nb_buttons = int.from_bytes(bytes_data[0:2], 'big')
        offset = 2
        for _ in range(nb_buttons):
            name_len = int.from_bytes(bytes_data[offset:offset+2], 'big')
            offset += 2
            name = bytes_data[offset:offset+name_len].decode('utf-8')
            offset += name_len
            ip_len = int.from_bytes(bytes_data[offset:offset+2], 'big')
            offset += 2
            ip = bytes_data[offset:offset+ip_len].decode('utf-8')
            offset += ip_len
            port = int.from_bytes(bytes_data[offset:offset+2], 'big')
            offset += 2
            self.add_server_to_list(name, ip, port)
        return offset


join_menu = ServerListMenu()
menu.register_menu(join_menu)


class MainMenu(menu.Menu):
    def __init__(self):
        super().__init__("main_menu")
        self.pause = True
        join_menu.back_but.menu = self
        Entity(model='quad', parent=self,texture='assets/textures/logo_color.png',scale=(0.5,0.25),position=(0,0.25,-0.1))
        self.te = menu.CustomTextField(
            max_lines=1, parent=self, scale=(0.38, 0.07),
            position=(0, 0.0, -0.1), text_size=1.5,
            naming_box="Nom du joueur :", bg_color=color.black,
            character_limit=16
        )
        self.multijoueur = menu.FixedButton(
            text='Jouer',
            scale=(0.35, 0.08),
            position=(0, -0.15), parent=self,
            text_size=2
        )
        self.multijoueur.on_click = self.switch(lambda: menu.show(join_menu))

        from ursina import application
        quit_btn = menu.FixedButton(
            parent=self, text='Quitter',
            text_color=color.dark_gray,
            highlight_text_color=color.dark_gray,
            scale=(0.35, 0.08), position=(0, -0.3),
            text_size=2,
        )
        quit_btn.on_click = application.quit
        self.color = color.white
        

    from typing import Callable
    def switch(self, button: 'Callable'):
        def default_switch():
            global _name
            _name = self.te.text_field.text
            if _name == "":
                _name = "player"
            self.hide()
            menu.rotate_page_and_run([button, lambda: self.show()])
        return default_switch
    

main_menu = MainMenu()
menu.show(main_menu)
menu.register_menu(main_menu)

def get_name():
    if _name == "player" and main_menu.te.text_field.text != "":
        return main_menu.te.text_field.text
    return _name

def set_name(name):
    global _name
    _name = name
    main_menu.te.text_field.text = name
    main_menu.te.text_field.render()