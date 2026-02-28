from client import data,menu,world
from ursina import Entity,color,Vec3,camera,TextField,Button,dedent,Text,ButtonList,Texture
from ursina.prefabs.dropdown_menu import DropdownMenu,DropdownMenuButton
from shared.utils import get_local_ip

name = "player"

class ServerButton(Button):
    def __init__(self, name, ip, port, parent):
        super().__init__(text=name, position=(0,0.5-len(parent.children)*0.1), scale=(0.4, 0.1), text_size=1,parent=parent)
        self._selected = False
        self.ip = ip
        self.port = port

    def on_click(self):
        if self.selected:
            self.selected = False
            self.connect()
        else:
            self.selected = True

    def connect(self):
        res = world.join_world(self.ip, self.port, "default")
        if res :
            print("Erreur : "+str(res))
            self.parent.show_error(res)
        else:
            menu.hide()
    
    @property
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self, value):
        self._selected = value
        if value:
            self.color = self.color.tint(-.5)
        else:
            self.color = self.color.tint(.5)

class AddServerMenu(menu.Menu):
    def __init__(self):
        super().__init__("join_menu")
        self.texterr = Text("format : ip:port (ex: localhost:5555)", parent=self, position=(-0.2, 0.1, -0.1), scale=0.5,color=color.red)
        self.te = menu.CustomTextField(max_lines=30,parent=self,scale=(0.4,0.1), position=(0, 0.15, -0.1), text_size=1, naming_box="Adresse Ip",bg_color=color.black)
        self.connect_but = Button(text='ajouter le serveur', position=(0,-0.1), scale=(0.4, 0.1), text_size=1,parent=self)
        self.connect_but.on_click = self.rejoindre
        self.server_list_menu : 'ServerListMenu' = None

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
        if self.server_list_menu is not None:
            self.server_list_menu.add_server_to_list(content, lst[0], int(lst[1]))
        else:
            print("Erreur : server_list_menu is None")
        menu.show(self.server_list_menu)

        

add_server = AddServerMenu()
menu.register_menu(add_server)

class ServerListMenu(menu.Menu):
    def __init__(self):
        super().__init__("server_list_menu")
        self.pause = True
        self.button_list = []
        add_server.server_list_menu = self
        self.back_but = menu.LinkingButton(menu=None,text='back', position=(-0.4,-0.3), scale=(0.4, 0.1), text_size=1,parent=self)
        self.add_server_but = menu.LinkingButton(menu=add_server,text='Ajouter un serveur', position=(0,-0.3), scale=(0.4, 0.1), text_size=1,parent=self)

    def add_server_to_list(self, name, ip, port):
        new_but = ServerButton(name, ip, port, self)
        self.button_list.append(new_but)

    def show_error(self, error):
        pass
        
join_menu = ServerListMenu()
menu.register_menu(join_menu)

class MainMenu(menu.Menu):
    def __init__(self):
        super().__init__("main_menu")
        self.pause = True
        join_menu.back_but.menu = self
        self.test = menu.LinkingButton(menu=join_menu,text='Multijoueur',scale=(0.4,0.1), text_size=1, position=(0,0.1),parent=self)
        te = menu.CustomTextField(max_lines=30,parent=self,scale=(0.4,0.1), position=(0,-0.1, -0.1), text_size=1, naming_box="Nom du joueur :",bg_color=color.black)
        te.parent = self
        self.te = te
        from ursina import application
        quit =Button(parent=self,text='Quitter', scale=(0.4, 0.1), position=(0,-0.3), text_size=1)
        quit.on_click = application.quit
        self.test.on_click = self.switch(self.test.on_click)

    from typing import Callable
    def switch(self, button:'Callable'):
        def default_switch():
            global name
            name = self.te.text_field.text
            if name == "":
                name = "player"
            button()
        return default_switch

main_menu = MainMenu()
menu.show(main_menu)
menu.register_menu(main_menu)


        