from ursina import *
from textwrap import dedent

app = Ursina()
window.color = color._25
te = TextField(max_lines=30, register_mouse_input=True)
te.text = dedent('''Lorem ipsum dolor sit amet...''')
te.bg.color = color.black
te.bg.scale = (0.3, 0.1)
te.render()

def input(key):
    if key == '3':
        te.input('scroll down')

EditorCamera()
app.run()