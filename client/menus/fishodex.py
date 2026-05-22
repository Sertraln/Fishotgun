import client.menu as menu
from client.world import World
from copy import deepcopy
from ursina import Entity,Text,color,time,camera
from shared.parsedata.fishlist import FishInventory
from shared.registry import fish_list, FishData, FishList, Rarity
import client.data as data

max_per_page = 6

class FishDisplay(Entity):
    def __init__(self,fish_instance:FishData,**kwargs):
        super().__init__(**kwargs)
        self.fish_instance = fish_instance
        self.model = "cube"
        self.texture = f"assets/fish/{fish_instance.name}.png"
        self._quantity = 0
        self._quantity_text = Text("",parent=self,position=(0,-0.5,0),scale=0.05,font=data.fisho_font,enabled=False)
        self.description = Text(fish_instance.description,parent=self,position=(0,0,-10),scale=10,enabled=False,color=color.white,font=data.fisho_font)
        self.description.wordwrap_setter(15)
        self.scale = (0.1,0.1,0.05)
        self.color = color.black
        self.ignore_paused = True
        self.collider = "box"

    @property
    def quantity(self):
        return self._quantity
    
    @quantity.setter
    def quantity(self, value):
        self._quantity = value
        self._quantity_text.text = "x"+str(self._quantity)
    
    def update(self):
        if self.hovered and not self.description.enabled:
            self.description.enable()
        elif not self.hovered and self.description.enabled:
            self.description.disable()

    def unlocked(self):
        self.color = color.white
        self._quantity_text.enabled = True

start_pos = (0.1,0.2)
hight_space = -0.2
width_space = -0.2
max_per_line = 2
base_offset = -0.1

class FishPage(Entity):
    def __init__(self,fish_list:list[FishData],is_left:bool,offset=0,**kwargs):
        super().__init__(**kwargs)
        self.fish_displays : list[FishDisplay] = []
        self._show_fish = True
        base_position = self.position
        self.page = Entity(parent=self,position=(self.position[0],self.position[1],0.0),texture="assets/ui/menu.png",scale=(0.75,0.923188406,0.0),model="cube")
        self.position = (0,0,self.position[2])
        self.dir = 1 if is_left else -1
        if is_left:
            self.page.rotation_y = 180
        for i,fish_data in enumerate(fish_list):
            fish_display = FishDisplay(fish_data,parent=self)
            fish_display.position = (start_pos[0]+base_position[0] + (i%max_per_line)*width_space,start_pos[1]+base_position[1] + (i%max_per_page//max_per_line)*hight_space,(i//max_per_page)*offset+base_offset)
            print(f"Fish {fish_data.name} position : {fish_display.position}")
            self.fish_displays.append(fish_display)

    def update_display(self,fish_inventory:FishInventory):
        for fish_display in self.fish_displays:
            if fish_inventory.fish_list.is_unlocked(fish_display.fish_instance.fishid):
                fish_display.unlocked()
                fish_display.quantity = fish_inventory.capacity[fish_display.fish_instance]

    @property
    def show_fish(self):
        return self._show_fish
    
    @show_fish.setter
    def show_fish(self, value):
        self._show_fish = value
        for fish_display in self.fish_displays:
            fish_display.enabled = value

class FishodexMenu(menu.Menu):
    def __init__(self):
        super().__init__("fishodex",False)
        self.parent = camera.ui
        self.leftpage = FishPage(fish_list[0:6],True,parent=self,name="leftpage",position=(-0.31,0,0.01))
        self.middlepage = FishPage(fish_list[6:18],False,0.2,parent=self,name="middlepage",position=(0.31,0,-0.15))
        self.rightpage = FishPage(fish_list[18:24],False,parent=self,name="rightpage",position=(0.31,0,0))
        self.rotation_direction = -1
        self.rotation_speed = 200
        self.next_button = menu.FixedButton(parent=self,text="Page suivante",position=(0.3,-0.4,0),scale=(0.2,0.1,1),on_click=self.rotate_middle_page)
        self.prev_button = menu.FixedButton(parent=self,text="Page précédente",position=(-0.3,-0.4,0),scale=(0.2,0.1,1),on_click=self.rotate_middle_page)
        self.prev_button.disable()

    def enable(self):
        super().enable()
        #self.rightpage.update_display(data.player.fish_inventory)

    def update(self):
        if self.enabled and self.middlepage.rotation_y+self.rotation_direction > 0 and self.middlepage.rotation_y+self.rotation_direction < 180:
            self.middlepage.rotation_y += self.rotation_speed * time.dt * self.rotation_direction
        elif not self.middlepage.show_fish:
            self.middlepage.show_fish = True
            if self.rotation_direction > 0:
                self.prev_button.enabled = True
                self.next_button.enabled = False
            else:
                self.prev_button.enabled = False
                self.next_button.enabled = True

    def rotate_middle_page(self):
        self.rotation_direction *= -1
        self.middlepage.rotation_y += self.rotation_direction
        self.middlepage.show_fish = False
        self.prev_button.enabled = False
        self.next_button.enabled = False

        

fishodexmenu = FishodexMenu()
menu.register_menu(fishodexmenu)