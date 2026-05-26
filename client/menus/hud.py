import client.menu as menu
from ursina import Text, Entity, color
import client.data as data
from typing import TYPE_CHECKING
from client.world import _world
if TYPE_CHECKING:
    from client.player import ThirdPersonController

class Hud(menu.Menu):
    def __init__(self):
        super().__init__("hud")
        self.scales = Entity(model="quad", texture="assets/textures/fish_scale.png", parent=self, position=(0.45, 0.4), scale=0.1)
        self.fishodex = Entity(model="quad", texture="assets/textures/fishodex.png", parent=self, position=(-0.75, 0), scale=(0.2,0.3), z=0)
        self.fishodex_text = Text(parent=self.fishodex, text="F", position=(-0.1, -0.2), scale=(14,10), color=color.white, font=data.fisho_font, z=-1)
        self.currency_text = Text(parent=self, text=": 0", position=(0.5, 0.4), origin = (-0.5, 0), scale=2, font=data.fisho_font)

    def update_currency(self, amount: int):
        self.currency_text.text = f": {amount}"

data.hud = Hud()