from ursina import *

chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?@#"

app = Ursina()

font_texture = load_texture('client/assets/textures/font/ascii.png')

text = Text(
    text="HELLO",
    texture=font_texture,
    scale=2
)