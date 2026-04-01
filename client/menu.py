from ursina import Button, mouse, Vec2,Vec3,Entity,camera,TextField,Text,color,application,InputField


class FixedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.text_entity:
            self.text_entity.position = Vec3(0,0,-1)

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
        self.menu = menu

    def on_click(self):
        show(self.menu)

_currentMenu : Menu = None

_menus : dict[str, Menu] = {}

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

    def __init__(self, bg_color=color.black,scale=(0.4,0.1), position=(0,0,0), text_color=color.white, naming_box=None, **kwargs):
        super().__init__(scale=scale,position=position,**kwargs)
        text_size = (1/scale[0],1/scale[1])
        self.text_field.text_entity.scale = 1/1.25
        self.text_field.text_entity.font = "assets/font/FishoFont.ttf"
        # self.bg.color = bg_color
        # self.bg.scale = scale
        self.text_color = text_color
        self.naming_box = None if naming_box is None else Text(text=naming_box, parent=self, position=(-0.5,0.9, -0.1), scale=text_size, color=text_color)
        # self.render()

    
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