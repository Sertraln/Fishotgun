from ursina import Button, mouse, Vec2,Entity,camera

class Menu(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.elements : list[Entity]  = []
        self.enabled = False
        self.pause = True

    def add_element(self, element : Entity):
        element.hide()
        self.elements.append(element)
        element.parent = self

    def isenabled(self):
        return self.enabled

    def display(self):
        self.enabled = True
        self.show()

    def hide(self):
        self.enabled = False
        self.hide()

class LinkingButton(Button):
    def __init__(self, menu : Menu, **kwargs):
        super().__init__(kwargs)
        self.menu = menu

    def on_click(self):
        show(self.menu)

_currentMenu : Menu = None

def show(menu : Menu):
    global _currentMenu
    if _currentMenu is not None:
        _currentMenu.hide()
    _currentMenu = menu
    menu.display()

def ispausing():
    return _currentMenu is not None and _currentMenu.pause

def hide():
    mouse.position = Vec2(0,0)
    global _currentMenu
    if _currentMenu is not None:
        _currentMenu.hide()
    _currentMenu = None


quit_button = Button(text='Quitter', color=(0,0,0,0.5), scale=(0.2, 0.1), position=(0,-0.1))
quit_button.hide()

def init():
    from ursina import application
    quit_button.on_click = application.quit

