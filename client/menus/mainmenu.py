from client import data,menu
from ursina import Entity,color,Vec3,camera,TextField,Button,dedent

class JoinMenu(menu.Menu):
    def __init__(self):
        super().__init__()
        self.pause = True
        te = TextField(max_lines=30, register_mouse_input=True)
        te.parent = self
        te.text = dedent('''Lorem ipsum dolor sit amet...''')
        te.bg.color = color.black
        te.bg.scale = (0.3, 0.1)
        te.render()
        self.connect_but = Button(text='rejoindre', position=(0,-0.1), scale=(0.4, 0.1), text_size=1,parent=self)

join_menu = JoinMenu()

class MainMenu(menu.Menu):
    def __init__(self):
        super().__init__()
        self.pause = True
        menu.LinkingButton(menu=join_menu,text='Multijoueur',scale=(0.4,0.1), text_size=1, position=(0,0.1),parent=self)
        from ursina import application
        quit =Button(parent=self,text='Quitter', scale=(0.4, 0.1), position=(0,-0.1), text_size=1)
        quit.on_click = application.quit

main_menu = MainMenu()
menu.show(main_menu)


        