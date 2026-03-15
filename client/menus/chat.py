import client.menu as menu
from ursina import Vec3, color, mouse,Texture,Entity
import client.data as data
from client.packet.serverbound import ServerBoundMessagePacket

class Chat(menu.Menu):
    def __init__(self):
        super().__init__("chat_menu",True)
        self.textfield = menu.InputField(scale=(2,0.2),position=(0,-0.4),parent=self)
        self.textfield.submit_on = ['enter']
        self.textfield.on_submit = self.send_message
        self.textfield.ignore_paused = True
        self.message_background = Entity(model='quad',scale=(2.2,0.6),color=color.black66,position=(0,0),parent=self) 
        self.message_display = menu.Text("",position=(0,0.3),parent=self)

    def send_message(self):
        text = self.textfield.text
        self.textfield.text = ""
        if text.strip() == "":
            return
        formated = f"{data.player.name}: {text}"
        self.add_message(formated)
        data.network.send(ServerBoundMessagePacket(formated))

    def add_message(self, message):
        self.message_display.text += message + "\n"
        # Limit the number of messages displayed to prevent overflow
        max_messages = 10
        if len(self.message_display.text.split("\n")) > max_messages:
            self.message_display.text = "\n".join(self.message_display.text.split("\n")[-max_messages:])

    def enable(self):
        self.textfield.active=True
        return super().enable()
    
    def disable(self):
        self.textfield.active=False
        return super().disable()