from ursina import *
from client import menu
from client.menu import FixedButton
from client.packet.serverbound import ServerBoundSellFishPacket
import client.data as data

class UpgradeItemMenu(menu.Menu):
    def __init__(self, max_level=10, **kwargs):
        super().__init__("upgrade", pause=True, anim=True)
        self.bg = Entity(parent=self, model='quad', color=color.rgba(0, 0, 0, 0.5), scale=(1.5, 0.8), position=(0, 0))
        self.btn_back = FixedButton(parent=self, text="Back", scale=(0.2, 0.1), position=(0, -0.3))
        self.btn_back.on_click = lambda: menu.show("shop")
        self.max_level = max_level
        self.icon = Entity(parent=self, model='quad', texture="assets/textures/Shotgun.png",scale=(0.6, 0.6), position=(-0.4, -0.1))
        self.btn = FixedButton(parent=self, text="Upgrade", color=color.white, text_size=1.5, position=(0.4, -0.3))
        self.btn.on_click = self.upgrade
        self.level_bar = Entity(parent=self, model='quad', color=color.white, scale=(0.05, 0.6), position=(-0.1, 0))
        self.progress_bar = Entity(parent=self.level_bar, model='quad', color=color.green, scale_y=0, origin_y=-0.5, position=(0, -0.5))
        self.dmg_text = Text(
            text="", 
            parent=self, 
            position=(-0.6, -0.35),
            scale=1.5, 
            color=color.white, 
            font=data.fisho_font
        )
        self.lvl_text = Text(
            text="", 
            parent=self, 
            position=(-0.6, -0.3),
            scale=1.5, 
            color=color.white, 
            font=data.fisho_font
        )
        self.price_text = Text(
            text="", 
            parent=self, 
            position=(0.4, -0.2),
            scale=1.5,
            font=data.fisho_font
        )
    
    def on_enable(self):
        self.update_level_bar()

    def get_dmg(self, level):
        return (level*5)

    def update_level_bar(self):
        if not data.player: return
        self.progress_bar.scale_y = data.player.level / self.max_level

        current_dmg = self.get_dmg(data.player.level)
        if data.player.level < self.max_level:
            next_dmg = self.get_dmg(data.player.level+1)
            self.dmg_text.text = f"{current_dmg} -> {next_dmg} DMG"
        else:
            self.dmg_text.text = f"{current_dmg} DMG (MAX)"

        if data.player.level < self.max_level:
            self.lvl_text.text = f"Lvl.{data.player.level}"
        else:
            self.lvl_text.text = f"Lvl.{data.player.level} (MAX)"
        
        if data.player.level < self.max_level:
            self.price_text.text = f"<image:assets/textures/fish_scale.png> {data.player.level * 1000}"
        else:
            self.price_text.text = ""

    def upgrade(self):
        if data.player.level < self.max_level:
            self.update_level_bar()

def hide_dialogue():
    menu.hide()
    mouse.locked = True

class ShopMenu(menu.Menu):
    def __init__(self):
        super().__init__("shop", pause=True)
        self.bg = Entity(parent=self, model='quad', color=color.rgba(0, 0, 0, 0.5), scale=(1.3, 0.4), position=(0, -0.3), z=0)
        self.npc_text_a = Text(text="Hey, t'as des poissons pour moi ?", color=color.white, position=(-0.6, -0.15), scale=1.5, font=data.fisho_font)
        self.npc_text_b = Text(text="Je commence à avoir faim...", color=color.white, position=(-0.6, -0.22), scale=1.5, font=data.fisho_font)
        self.btn_sell = FixedButton(text="Vendre tous les poissons - 0$", color=color.white, position=(-0.57, -0.33), scale=(0.3, 0.1), origin=(-0.5, 0))
        self.btn_buy = FixedButton(text="Acheter une amélioration", color=color.white, position=(-0.6, -0.4), scale=(0.3, 0.1), origin=(-0.5, 0))
        self.btn_quit = FixedButton(text="Quitter", color=color.white, position=(-0.72, -0.47), scale=(0.3, 0.1), origin=(-0.5, 0))

        for btn in [self.npc_text_a, self.npc_text_b, self.btn_sell, self.btn_buy, self.btn_quit]:
            btn.origin = (-0.5, 0)
            self.add_element(btn)
            btn.set_bin('fixed', 1)

        self.enabled = False      

        self.btn_sell.on_click = self.sell_fish
        self.btn_buy.on_click = self.buy_upgrade
        self.btn_quit.on_click = hide_dialogue

    def update_sell_button(self):
        total = 0
        if hasattr(data, 'player') and hasattr(data.player, 'fish_inventory'):
            total = data.player.fish_inventory.get_total_price()  
        self.btn_sell.text = f"Vendre tous les poissons - {total}$"

    def sell_fish(self):
        data.network.send(ServerBoundSellFishPacket())

        if hasattr(data, 'player') and hasattr(data.player, 'fish_inventory'):
            data.player.fish_inventory.clear_inventory()

        self.update_sell_button()

    def buy_upgrade(self):
        menu.show("upgrade")

menu.register_menu(UpgradeItemMenu())
menu.register_menu(ShopMenu())

def open_shop_dialogue():
    mouse.locked = False
    menu.show("shop")