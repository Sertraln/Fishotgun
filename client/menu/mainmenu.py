from client import data,menu
from ursina import Entity,color,Vec3,camera,TextField,Button

class JoinMenu(menu.Menu):
    def __init__(self):
        super().__init__()
        self.pause = True
        self.hide()
        self.ip_field = TextField(text='addresse', parent=self, position=(0,0.1), scale=(0.3,0.1))

join_menu = JoinMenu()

class MainMenu(menu.Menu):
    def __init__(self):
        super().__init__()
        self.pause = True
        self.hide()
        menu.LinkingButton(menu=join_menu,text="Multijoueur",parent=self,max_lines=64, line_height=1.1, character_limit=None)
        quitter = menu.quit_button.copy_to(self)
        quitter.position = (0,-0.1)

    def join_menu(self):
        menu.show(join_menu)


main_menu = MainMenu()


        