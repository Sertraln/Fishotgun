from ursina import Button

class Menu:
    def __init__(self):
        self.buttons : list[Button]  = []

    def add_button(self, button):
        self.buttons.append(button)

    def display(self):
        for button in self.buttons:
            button.show()

    def hide(self):
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
    currentMenu.hide()
    currentMenu = menu
    menu.display()