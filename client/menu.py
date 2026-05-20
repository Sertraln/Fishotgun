from ursina import Button, mouse, Vec2,Vec3,Entity,camera,TextField,Text,color,application,InputField,Shader,time,Texture
import client.data as data
from panda3d.core import SamplerState

def set_color():
    return f'''
#version 120

uniform sampler2D p3d_Texture0;
uniform vec3 color;

varying vec2 uv;
    
void main() {{
     gl_FragColor = vec4(1.0)*texture2D(p3d_Texture0, uv) + vec4(color,0.0);
}}

'''

def set_static_color(color:color):
    return f'''
#version 120

uniform sampler2D p3d_Texture0;

varying vec2 uv;
    
void main() {{
     gl_FragColor = vec4(1.0)*texture2D(p3d_Texture0, uv) + vec4({color[0]},{color[1]},{color[2]},0.0);
}}

'''


class FixedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.text_entity:
            self.text_entity.position = Vec3(0,0,-1)
            self.text_entity.font = data.fisho_font
            print(type(self.text_entity))  # vérifie le type
            print(self.children)
            test = Shader(fragment=set_color(),vertex=data.default_vertex)
            self.text_entity.set_shader_input("color",color.white)
            self.model.hide()
            test.compile()
            self.text_entity.shader = test
        self.ignore_paused = True
            
    def update(self):
        if self.text_entity:
            self.text_entity.set_shader_input("color",self.model.get_color_scale())

class BackGround(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui,position=(0,0,1),scale=(1,1,1),ignore_paused=True)
        self.paper_pivot = Entity(parent=self,name="pivot",position=(-0.3,0,1))
        self.fake_paper = Entity(parent=self,model="cube",
                            scale=(0.8,0.9,0.0),color=color.white,texture="assets/ui/menu.png",
                            ignore_paused=True,position=(0,0,1.01))
        self.paper = Entity(parent=self.paper_pivot,model="cube",
                            scale=(0.8,0.9,0.0),color=color.white,texture="assets/ui/menu.png",
                            ignore_paused=True,position=(0.3,0,0))
        self.paper._texture._texture.setMagfilter(SamplerState.FT_nearest)
        self.paper.parent = self.paper_pivot
        self.backgound = Entity(model="cube",parent=camera.ui,position=(0,0,4),rotation=(0,0,0),
                                texture="assets/ui/menu_bg.png",scale=(2,1,0.1),ignore_paused=True)
        self.paper._texture._texture.setMagfilter(SamplerState.FT_nearest)
        self.rotate_page = False
        self.to_run = []
        self.rotation_direction = 1
        self.rotation_speed = 400
        
    def update(self):
        if self.rotate_page:
            self.paper_pivot.rotation_y += self.rotation_speed * self.rotation_direction * time.dt
            if self.paper_pivot.rotation_y >= 350 or self.paper_pivot.rotation_y <= -350:
                self.paper_pivot.rotation_y = 0
                self.rotate_page = False
                for func in self.to_run:
                    func()
                self.to_run = []

    def rotate_and_run(self,func,rotation_direction=1):
        self.rotate_page = True
        self.to_run = func
        self.rotation_direction = rotation_direction

class Menu(Entity):
    def __init__(self,id:str,pause=True):
        super().__init__(parent=camera.ui,position=(0,0,0),scale=(1,1,0),ignore_paused=True,enabled=False)
        self.elements : list[Entity]  = []
        self.pause = pause
        self.id :str = id
        self.ignore_paused = True

    def add_element(self, element : Entity):
        self.elements.append(element)
        element.parent = self

    def update(self):
        for child in self.children:
            if isinstance(child, FixedButton) and hasattr(child, 'text_entity') and child.text_entity:
                child.text_entity.color = color.white

class LinkingButton(FixedButton):
    def __init__(self, menu : Menu, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key ,value)
        self.text_entity.color = color.black
        self.color = color.black
        self.menu = menu

    def on_click(self):
        show(self.menu)

_currentMenu : Menu = None

_menus : dict[str, Menu] = {}

_background_menu = BackGround()

def register_menu(menu : Menu):
    global _menus
    _menus[menu.id] = menu

def show(menu : Menu | str):
    if isinstance(menu, str):
        global _menus
        print(_menus)
        menu = _menus[menu]
    global _currentMenu
    if _currentMenu is not None:
        _currentMenu.disable()
    _currentMenu = menu
    menu.enable()
    application.paused = menu.pause

def ispausing():
    return _currentMenu is not None and _currentMenu.pause

def hide():
    mouse.position = Vec2(0,0)
    global _currentMenu
    if _currentMenu is not None:
        _currentMenu.disable()
    _currentMenu = None
    application.resume()


quit_button = FixedButton(text='Quitter', scale=(0.2, 0.1), position=(0,-0.1))
quit_button.disable()

class CustomTextField(InputField):

    def __init__(self, bg_color=color.black,scale=(0.4,0.1), position=(0,0,0), text_color=color.black, naming_box=None, **kwargs):
        super().__init__(scale=scale,position=position,**kwargs)
        text_size = (1/scale[0],1/scale[1])
        self.text_field.text_entity.scale = 1/1.25
        self.text_field.text_entity.font = data.fisho_font
        self.ignore_paused = True
        self.text_color = text_color
        self.naming_box = None if naming_box is None else Text(text=naming_box, parent=self, position=(-0.5,0.9, -0.1),
                                                                scale=text_size, color=text_color, font = data.fisho_font)
        self.model.set_scale((1,0.1,0.01))
        self.model.set_pos(0,-0.2,0.2)
        self.text_field.cursor.model.set_y(0.2)
        self.text_field.cursor.color = text_color
        self.text_field.color = text_color
        self.highlight_text_color = text_color
    
    def update(self):
        # N'exécute le code du parent que si certaines conditions sont vraies
        if self.parent and isinstance(self.parent, Menu):
            self.active = self.parent.enabled

    @property
    def text(self):
        return self.text_field.text

def getMenu(menu_id:str) -> Menu | None:
    global _menus
    return _menus.get(menu_id)

def init():
    from ursina import application
    quit_button.on_click = application.quit
    import client.menus.mainmenu as mainmenu

def rotate_page_and_run(func : list[callable],rotation_speed=1):
    if _background_menu.enabled:
        _background_menu.rotate_and_run(func,rotation_speed)