import client.menu as menu
from ursina import Text, Entity
import client.data as data
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client.player import ThirdPersonController

class Hud(menu.Menu):
    def __init__(self):
        super().__init__("hud")
        self.scales = Entity(model="quad", texture="assets/textures/fish_scale.png", parent=self, position=(0.3, 0.4), scale=0.1)
        self.currency_text = Text(parent=self, text=": 0", position=(0.5, 0.4), origin=(0, 0.5), scale=2, font=data.fisho_font)

    def update_currency(self, amount: int):
        self.currency_text.text = f": {amount}"

data.hud = Hud()