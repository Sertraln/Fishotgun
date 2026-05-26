import client.menu as menu
from ursina import Text
import client.data as data
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client.player import ThirdPersonController

class Hud(menu.Menu):
    def __init__(self):
        super().__init__("hud")
        self.currency_text = Text(parent=self, text="<image:assets/textures/fish_scale>: 0", position=(0.5, 0.4), origin=(0, 0.5), scale=2, font=data.fisho_font)

    def update_currency(self, amount: int):
        self.currency_text.text = f"<image:assets/textures/fish_scale>: {amount}"

data.hud = Hud()