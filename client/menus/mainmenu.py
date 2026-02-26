from client import data,menu,world
from ursina import Entity,color,Vec3,camera,TextField,Button,dedent,Text
from shared.utils import get_local_ip

class JoinMenu(menu.Menu):
    def __init__(self):
        super().__init__("join_menu")
        self.pause = True
        text = Text("adresse ip :", parent=self, position=(-0.2, 0.23, -0.1), scale=1)
        self.texterr = Text("format : ip:port (ex: localhost:5555)", parent=self, position=(-0.2, 0.15, -0.1), scale=0.5,color=color.red)
        te = TextField(max_lines=30)
        te.parent = self
        te.bg.color = color.black
        te.bg.scale = (0.4, 0.1)
        te.bg.position = (0,0, 0.1)
        te.position = (-0.2, 0.2, -0.1)
        te.render()
        self.te = te
        self.connect_but = Button(text='rejoindre', position=(0,-0.1), scale=(0.4, 0.1), text_size=1,parent=self)
        self.connect_but.on_click = self.rejoindre

    def rejoindre(self):
        content = self.te.text
        lst = content.split(":")
        size = len(lst)
        if lst[0] == "":
            lst = [get_local_ip(),"5555"]
        if size == 1:
             lst.append("5555")
        if lst[0] == "localhost":
            lst[0] = get_local_ip()
        print(f"Rejoindre {lst[0]}:{lst[1]}")
        res = world.join_world(lst[0], int(lst[1]), "default")
        if res :
            self.texterr.text = "Erreur : "+str(res)
        else:
            menu.hide()

join_menu = JoinMenu()
menu.register_menu(join_menu)

class MainMenu(menu.Menu):
    def __init__(self):
        super().__init__("main_menu")
        self.pause = True
        menu.LinkingButton(menu=join_menu,text='Multijoueur',scale=(0.4,0.1), text_size=1, position=(0,0.1),parent=self)
        from ursina import application
        quit =Button(parent=self,text='Quitter', scale=(0.4, 0.1), position=(0,-0.1), text_size=1)
        quit.on_click = application.quit

main_menu = MainMenu()
menu.show(main_menu)
menu.register_menu(main_menu)


        