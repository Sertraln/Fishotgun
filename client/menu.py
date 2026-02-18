from ursina import Button, mouse, Vec2,Entity,camera

class Menu(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui,position=(0,0,0),scale=(1,1,0))
        self.elements : list[Entity]  = []
        self.enabled = False
        self.pause = True

    def add_element(self, element : Entity):
        self.elements.append(element)
        element.parent = self

    def isenabled(self):
        return self.enabled

class LinkingButton(Button):
    def __init__(self, menu : Menu, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key ,value)
        self.menu = menu

    def on_click(self):
        show(self.menu)

_currentMenu : Menu = None

def show(menu : Menu):
    global _currentMenu
    if _currentMenu is not None:
        _currentMenu.disable()
    _currentMenu = menu
    menu.enable()

def ispausing():
    return _currentMenu is not None and _currentMenu.pause

def hide():
    mouse.position = Vec2(0,0)
    global _currentMenu
    if _currentMenu is not None:
        _currentMenu.disable()
    _currentMenu = None


quit_button = Button(text='Quitter', scale=(0.2, 0.1), position=(0,-0.1))
quit_button.disable()

def init():
    from ursina import application
    quit_button.on_click = application.quit
    import client.menus.mainmenu as mainmenu

