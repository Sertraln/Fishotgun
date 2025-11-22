import socket
from packet.packetstruct import ClientBoundPacket,ServerBoundPacket
from packet.packetlib import getServerBoundPacket
import threading as th

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Server

class Client:
    def __init__(self,conn:socket.socket,ip ,id:int,server:'Server'):
        self.ip = ip
        self.conn = conn
        self.id = id
        self.thread = th.Thread(name="client"+str(self.id),target=self.paketListener)
        self.server = server
        self.stopevent = self.server.stopevent
        

    def send(self,packet:ClientBoundPacket):
        packet.send(self.conn)

    def sendRecv(self,packet:ClientBoundPacket) -> ServerBoundPacket:
        print("packet : sending",flush=True)
        packet.send(self.conn)
        return getServerBoundPacket(self.conn.recv(2048))
    
    def paketListener(self):
        try:
            while not self.stopevent.is_set():
                try:
                    print("server packet : listening player :", self.id)
                    data = self.conn.recv(2048)
                    if not data:
                        print(f"server packet : connection closed {self.id}")
                        break
                    
                    packets = getServerBoundPacket(data)
                    for packet in packets:
                        print("packet : handeled", packet.get_id())
                        packet.handle(self)
                except ConnectionResetError:
                    print(f"server packet : connection reset by client {self.id}")
                    break
                except Exception as e:
                    print(f"packet : error handling: {e}")
        finally:
            try:
                self.server.game.left_player(self.id)
                self.conn.close()
            except:
                pass
    
    def kick(self):
        self.stopevent.set()
        self.conn.close()

