import client.menu as menu
from ursina import color, Entity, Text, invoke, clamp
import client.data as data
from client.packet.serverbound import ServerBoundMessagePacket

class Chat(menu.Menu):
    def __init__(self):
        super().__init__("chat",True)
        self.textfield = menu.InputField(scale=(0.7,0.1),position=(-0.5,-0.4),parent=self,character_limit=None)
        self.textfield.submit_on = ['enter']
        self.textfield.on_value_changed = self._sync_text_state
        self.textfield.on_submit = self.send_message
        self.textfield.ignore_paused = True
        self.textfield.text_field.cursor.position = (0,0,-0.1)
        self.message_background = Entity(model='quad',scale=(0.8,0.6),color=color.black66,position=(-0.5,0),parent=self)
        self.message_display = Text(text="",position=(-0.85,-0.25), parent=self,)
        self.message_display.text_colors = {"player": color.orange, "default": color.white}
        self.messages = []
        self.message_display
        self.max_lines = 40
        self.max_characters = 24
        self.line_step = 0.025
        self.full_text = ""
        self._visible_start = 0

        self.textfield.text_field.render = self._render_text_window
        self.textfield.text_field.render()

    def _sync_text_state(self):
        self.full_text = self.textfield.text_field.text

    def _render_text_window(self):
        text_field = self.textfield.text_field
        self._sync_text_state()

        cursor_x = int(text_field.cursor.x)
        text_len = len(self.full_text)
        cursor_x = clamp(cursor_x, 0, text_len)

        if text_len <= self.max_characters:
            self._visible_start = 0
        else:
            if cursor_x < self._visible_start:
                self._visible_start = cursor_x
            elif cursor_x > self._visible_start + self.max_characters:
                self._visible_start = cursor_x - self.max_characters

            max_start = max(0, text_len - self.max_characters)
            self._visible_start = clamp(self._visible_start, 0, max_start)

        visible_end = self._visible_start + self.max_characters
        visible_text = self.full_text[self._visible_start:visible_end]

        text_field.text_entity.text = visible_text
        text_field.cursor_parent.x = -self._visible_start

    def send_message(self):
        text = self.full_text
        self.textfield.text = ""
        self.full_text = ""
        self._visible_start = 0
        self.textfield.text_field.cursor_parent.x = 0
        self.textfield.text_field.render()
        menu.hide()
        if text.strip() == "":
            return
        data.network.send(ServerBoundMessagePacket(text))

    def add_message(self,origine, message):
        # Limit the number of messages displayed to prevent overflow
        self.messages.append(f"<player>{origine}: <default>{message}")
        self.message_display.text = "\n".join(self.messages[-self.max_lines:])
        self.message_display.wordwrap_setter(54)
        if self.message_display.y < self.max_lines*self.line_step:
            self.message_display.y += self.line_step*len(self.message_display.lines)

    def enable(self):
        self.textfield.active=True
        return super().enable()
    
    def disable(self):
        self.textfield.active=False
        return super().disable()
    
    def input(self,key):
        text_field = self.textfield.text_field
        shortcuts = text_field.shortcuts

        move_ops = shortcuts['move_operations']
        should_refresh = (
            key in move_ops['move_up']
            or key in move_ops['move_down']
            or key in move_ops['move_right']
            or key in move_ops['move_left']
            or key in move_ops['move_to_start_of_word']
            or key in move_ops['move_to_end_of_word']
        )
        if should_refresh:
            invoke(text_field.render, delay=0)