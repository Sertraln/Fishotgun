import client.menu as menu
from ursina import Vec3, color, mouse

class Chat(menu.Menu):
    def __init__(self):
        super().__init__("chat_menu",True)
        self.textfield = menu.InputField(scale=(2,0.2),position=(0,-0.4),parent=self)
        self.textfield.ignore_paused = True

    def send_message(self, message:str):
        pass

    def enable(self):
        self.textfield.active=True
        return super().enable()
    
    def disable(self):
        self.textfield.active=False
        return super().disable()