import client.menu as menu
from ursina import Vec3, color, mouse,Texture,Entity,Text
import client.data as data
from client.packet.serverbound import ServerBoundMessagePacket

class Chat(menu.Menu):
    def __init__(self):
        super().__init__("chat",True)
        self.textfield = menu.InputField(scale=(0.7,0.1),position=(-0.5,-0.4),parent=self)
        self.textfield.submit_on = ['enter']
        self.textfield.on_submit = self.send_message
        self.textfield.ignore_paused = True
        self.message_background = Entity(model='quad',scale=(0.8,0.6),color=color.black66,position=(-0.5,0),parent=self) 
        self.message_display = Text("",position=(-0.85,0.3),parent=self)
        self.message_display.origin = (-0.5,0.5)
        self.message_display.text_colors = {'default': color.azure, 'player': color.orange}

    def send_message(self):
        text = self.textfield.text
        self.textfield.text = ""
        if text.strip() == "":
            return
        data.network.send(ServerBoundMessagePacket(text))
        menu.hide()

    def add_message(self,origine, message):
        self.message_display.text += Text.start_tag+'player'+Text.end_tag+origine+ ' > ' +Text.start_tag+'default'+Text.end_tag+ message + "\n"
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