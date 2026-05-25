import socket
from server.packet.packetstruct import ClientBoundPacket,ServerBoundPacket
from server.packet.packetlib import getServerBoundPacket
import threading as th
from shared.packetlib import HandlelingExeption,ParsingException,UncompletePacketException

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
        self.buffer = b""
        

    @property
    def player(self):
        return self.server.world.players.get(self.id)

    def send(self,packet:ClientBoundPacket):
        try:
            packet.send(self.conn)
        except Exception as e:
            print(f"client send error : {e}")

    def sendRecv(self,packet:ClientBoundPacket) -> ServerBoundPacket:
        print("packet : sending",flush=True)
        packet.send(self.conn)
        (result,self.buffer) = getServerBoundPacket(self.buffer+self.conn.recv(2048))
        while self.buffer:
            more_result,self.buffer = getServerBoundPacket(self.buffer)
            result.extend(more_result)
        return result
    
    def paketListener(self):
        try:
            while not self.stopevent.is_set():
                try:
                    print("server packet : listening player :", self.id)
                    data = self.conn.recv(2048)
                    if not data:
                        print(f"server packet : connection closed {self.id}")
                        break
                    data = self.buffer + data
                    self.buffer = b""
                    try:
                        packets,self.buffer = getServerBoundPacket(data)
                    except Exception as e:
                        raise ParsingException(f"error parsing packet from client {self.id} : {e} : data:{data}")
                    for packet in packets:
                        print("packet : handeled", packet.get_id())
                        try:
                            packet.handle(self)
                        except Exception as e:
                            raise HandlelingExeption(f"error handling packet from client {self.id} : {e} : packet:{packet}")
                except ConnectionResetError:
                    print(f"server packet : connection reset by client {self.id}")
                    break
                except HandlelingExeption as e:
                    print(e)
                except ParsingException as e:
                    print(e)
        finally:
            try:
                self.kick()
            except:
                pass
    
    def kick(self):
        self.server.world.left_player(self.id)
        self.conn.close()
        

