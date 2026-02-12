from ursina import Button, mouse, Vec2

class Menu:
    def __init__(self):
        self.buttons : list[Button]  = []
        self.enabled = False
        self.pause = True

    def add_button(self, button : Button):
        button.hide()
        self.buttons.append(button)

    def isenabled(self):
        return self.enabled

    def display(self):
        self.enabled = True
        for button in self.buttons:
            button.show()

    def hide(self):
        self.enabled = False
        for button in self.buttons:
            button.hide()

class linking_menu(Button):
    def __init__(self, menu : Menu):
        super().__init__(text='Linking Menu', color=(0,0,0,0.5), scale=(0.2, 0.1))
        self.menu = menu
        self.hide()

    def on_click(self):
        show(self.menu)

currentMenu : Menu = None

def show(menu : Menu):
    global currentMenu
    if currentMenu is not None:
        currentMenu.hide()
    currentMenu = menu
    menu.display()

def ispausing():
    return currentMenu is not None and currentMenu.pause

def hide():
    mouse.position = Vec2(0,0)
    global currentMenu
    if currentMenu is not None:
        currentMenu.hide()
    currentMenu = None

