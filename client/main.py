from ursina import *
from player import ThirdPersonController
from spot import FishingSpot
from fish import FishingScene
from transitions import IrisTransition

app = Ursina()

ground = Entity(
    model='cube',
    scale=(100,1,100),
    texture='grass',
    texture_scale=(10,10),
    collider='box')

player = ThirdPersonController(
    position=(0,4,0),
    jump_height=5,
    jump_up_duration=1,
    fall_after=.4,
    gravity=0.7)

player.cursor.color = color.white

spot = FishingSpot(position=(0,2,0))

iris = IrisTransition(close_duration=0.8, black_duration=0.5, open_duration=0.8)

def enter_fishing():
    iris.play(on_black=_enter_black)

def _enter_black():
    player.disable()
    mouse.locked = False
    fishing_scene.start()

def on_fishing_end(result):
    iris.play(on_black=_exit_black)

def _exit_black():
    fishing_scene.stop()
    player.enable()
    mouse.locked = True

fishing_scene = FishingScene(on_end=on_fishing_end)
spot.set_scene(fishing_scene)

Sky(color=color.violet)

def update():
    iris.update()

    if fishing_scene.enabled:
        fishing_scene.update()
        return

    if player.y < -10:
        player.position = (0, 4, 0)

    if held_keys['shift']:
        player.body.color = color.red
        player.speed = 20
    else:
        player.body.color = color.blue
        player.speed = 10

    if distance(spot.position, player.position) < spot.interaction_range:
        if held_keys['e']:
            enter_fishing()
        else:
            spot.color = color.yellow
    else:
        spot.color = color.white

app.run()