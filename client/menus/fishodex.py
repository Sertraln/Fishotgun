import client.menu as menu
from client.world import World
from copy import deepcopy
from ursina import Entity,Text

class FishDisplay(Entity):
    def __init__(self,fish_name:str,description:str,**kwargs):
        super().__init__(**kwargs)
        self.fish_name = fish_name
        self.model = "cube"
        self.texture = f"assets/fish/{fish_name}.png"
        self.description = Text(description,parent=self,position=(0,-0.5,0),scale=0.05,wordwrap=10)
        self.scale = (0.5,0.5,0.5)
    
    def update(self):
        if self.hovered:
            self.description.enabled = True
        else:
            self.description.enabled = False

class FishPage(Entity):
    def __init__(self,fish_list:list[tuple[str,str]],right:bool,**kwargs):
        super().__init__(**kwargs)
        self.fish_displays = []
        for i,(fish_name, description) in enumerate(fish_list):
            fish_display = FishDisplay(fish_name,description,parent=self)
            fish_display.position = (-0.5 + i%3*0.5,-0.5 + int(i/3)*0.5,0)
            self.fish_displays.append(fish_display)

class FishodexMenu(menu.Menu):
    def __init__(self):
        super().__init__("fishodex",False)
        self.unlocked_fish: list[str] = []
        self.rightpage = Entity(parent=self,name="rightpage",position=(0,0,1.01),texture="assets/ui/menu.png")
        self.leftpage = Entity(parent=self,name="leftpage",position=(0,0,1.01),texture="assets/ui/menu.png",rotation=(0,180,0))
        self.pivot = Entity(parent=self,name="pivot",position=(0,0,1))
        self.middlepage = Entity(parent=self.pivot,name="middlepage",position=(0,0,1),texture="assets/ui/menu.png") 
        self.max_per_page = 9
    
    def set_unlocked_fish(self,fish_list:list[tuple[str,str]]):
        for i,(fish_name, description) in enumerate(fish_list):
            if fish_name not in self.unlocked_fish:
                self.unlocked_fish.append(fish_name)
                fish_display = FishDisplay(fish_name,description,parent=self)
                fish_display.position = (-0.5 + i%3*0.5,-0.5 + int(i/3)*0.5,0)

fishodexmenu = FishodexMenu()