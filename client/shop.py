from ursina import *
from client import menu
from client.menu import FixedButton
from client.packet.serverbound import ServerBoundSellFishPacket
import client.data as data

class UpgradeItem(Entity):
    def __init__(self, name, level, max_level=10, **kwargs):
        super().__init__(**kwargs)
        self.level = level
        self.max_level = max_level
        self.icon = Entity(parent=self, model='quad', scale=(0.3, 0.3), position=(-0.4, 0))
        self.btn = Button(parent=self, text="Upgrade", scale=(0.2, 0.1), position=(0.4, 0))
        self.btn.on_click = self.upgrade
        self.level_bar = Entity(parent=self, model='quad', color=color.gray, scale=(0.05, 0.4), position=(0.15, 0))
        self.progress_bar = Entity(parent=self.level_bar, model='quad', color=color.green, scale_y=0, origin_y=-0.5, position=(0, -0.5))
        self.update_level_bar()

    def update_level_bar(self):
        self.progress_bar.scale_y = self.level / self.max_level

    def upgrade(self):
        if self.level < self.max_level:
            self.level += 1
            self.update_level_bar()

class UpgradeMenu(menu.Menu):
    def __init__(self):
        super().__init__("upgrade", pause=True)
        self.bg = Entity(parent=self, model='quad', color=color.rgba(0, 0, 0, 0.5), scale=(1.5, 0.8), position=(0, 0))
        self.shotgun_item = UpgradeItem(name="Shotgun", level=1, parent=self, position=(0, 0.1))
        self.add_element(self.shotgun_item)
        self.btn_back = FixedButton(text="Back", scale=(0.2, 0.1), position=(0, -0.3))
        self.btn_back.on_click = lambda: menu.show("shop")
        self.add_element(self.btn_back)

class ShopMenu(menu.Menu):
    def __init__(self):
        super().__init__("shop", pause=True)
        self.bg = Entity(parent=self, model='quad', color=color.rgba(0, 0, 0, 0.5), scale=(1.3, 0.4), position=(0, -0.3), z=0)
        self.npc_text_a = Text(text="Hey, t'as des poissons pour moi ?", color=color.white, position=(-0.6, -0.15), scale=1.5, font=data.fisho_font)
        self.npc_text_b = Text(text="Je commence à avoir faim...", color=color.white, position=(-0.6, -0.2), scale=1.5, font=data.fisho_font)
        self.btn_sell = FixedButton(text="Vendre tous les poissons - 0$", color=color.white, position=(-0.6, -0.35), scale=(0.3, 0.1), origin=(-0.5, 0))
        self.btn_buy = FixedButton(text="Acheter une amélioration", color=color.white, position=(-0.6, -0.40), scale=(0.3, 0.1), origin=(-0.5, 0))

        for btn in [self.npc_text_a, self.npc_text_b, self.btn_sell, self.btn_buy]:
            btn.origin = (-0.5, 0)
            self.add_element(btn)
            btn.set_bin('fixed', 1)

        self.enabled = False      

        self.btn_sell.on_click = self.sell_fish
        self.btn_buy.on_click = self.buy_upgrade

    def update_sell_button(self):
        total = 0
        if hasattr(data, 'player') and hasattr(data.player, 'fish_inventory'):
            total = data.player.fish_inventory.get_total_price()  
        self.btn_sell.text = f"Vendre tous les poissons - {total}$"

    def on_enable(self):
        self.update_sell_button()

    def sell_fish(self):
        data.network.send(ServerBoundSellFishPacket())
        self.btn_sell.text = "Vendre tous les poissons - 0$"

    def buy_upgrade(self):
        menu.show("upgrade")

menu.register_menu(UpgradeMenu())
menu.register_menu(ShopMenu())

def open_shop_dialogue():
    mouse.locked = False
    menu.show("shop")