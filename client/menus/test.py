from ursina import *

app = Ursina()

ZONE_TOP = 0.25
ZONE_BOTTOM = -0.25

# Frame décoratif
frame = Entity(
    parent=camera.ui,
    model='quad',
    color=color.dark_gray,
    scale=(0.4, 0.55),
    position=(0, 0, 1)  # z=1 pour être derrière les boutons
)

scroll_container = Entity(parent=camera.ui)
scroll_offset = 0

buttons = []
for i in range(15):
    b = Button(
        text=f'Option {i}',
        parent=camera.ui,
        scale=(0.18, 0.04),
        position=(0, ZONE_TOP - i * 0.055, 0),
        color=color.gray
    )
    buttons.append(b)

def input(key):
    global scroll_offset
    if key == 'scroll up':
        scroll_offset += 0.05
    elif key == 'scroll down':
        scroll_offset -= 0.05
    scroll_offset = clamp(scroll_offset, -0.6, 0)

    for i, b in enumerate(buttons):
        b.y = ZONE_TOP - i * 0.055 + scroll_offset
        # Masque si hors zone
        b.visible = ZONE_BOTTOM < b.y < ZONE_TOP
        b.collision = b.visible

app.run()