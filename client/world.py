from client import data,menu,network
from spot import FishingSpot
from ursina import application,Button,Entity,color,Sky

class World:
    def add_entity(self, entity: Entity):
        pass

def join_world(ip:str, port:int, name:str):
    try:
        data.network = network.Network(ip,port,name)
    except Exception as e:
        return e
    load_world()
    return None

def load_world():
    sky = Sky(color=color.violet)
    ground = Entity(
        model='cube',
        scale=(100,10,100),
        texture='grass',
        texture_scale=(10,10),
        collider='box')
    data.world = World()
    data.world.add_entity(ground)

    from client.data import player
    from client.player import ThirdPersonController

    player = ThirdPersonController(
        position=(0,4,0),
        jump_height = 5,
        jump_up_duration = 1,
        fall_after = .4,
        gravity = 0.7)
    
    data.player = player

    spot = FishingSpot(position=(0,2,0))

    data.world_entities = [sky, ground, spot]

    menu1 = menu.Menu("menu1")
    resume = Button(text='Resume', scale=(0.3, 0.1), position=(0,0.1))
    resume.on_click = menu.hide
    menu1.add_element(resume)
    quit = Button(text='Quit', scale=(0.3, 0.1), position=(0,-0.1))
    quit.on_click = quit_to_menu
    menu1.add_element(quit)
    menu.register_menu(menu1)

def quit_to_menu():
    from ursina import destroy
    from client.player import player_map

    menu.show("main_menu")

    if data.network:
        data.network.disconnect()
        data.network = None

    if data.player:
        data.player.disable()
        destroy(data.player)
        data.player = None

    for p in list(player_map.values()):
        p.disable()
        destroy(p)
    player_map.clear()

    for e in data.world_entities:
        destroy(e)
    data.world_entities = []

    if 'menu1' in menu._menus:
        destroy(menu._menus['menu1'])
        del menu._menus['menu1']

    data.world = None