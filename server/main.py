import socket
import os
import sys

# Ensure project root is on sys.path so sibling packages like `shared` can be imported
_ROOT = os.path.dirname(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from server.player import Player
import threading as th
from server.client import Client
from server.packet.serverbound import ServerBoundPseudoPacket
from server.packet import clientbound as cb
from server.world import World
import server.data as data

def get_local_ip():
    #ON NE TOUCHE PAS
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"
    
class Server:
    used_ports = []
    def __init__(self, port:int =5555, ip:str = None):
        #ON NE TOUCHE PAS
        from server.packet.packetlib import init_packetlib
        init_packetlib()
        self.port = port if port not in Server.used_ports else 5555+len(Server.used_ports)
        self.ip = ip if ip else get_local_ip()
        self.soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.threadlist : list[th.Thread] = []
        self.lastpid = 0
        self.stopevent = th.Event()
        self.world = World()
        try:
            self.soket.bind((self.ip, port))
        except socket.error as e:
            print("server :error binding :",e)
        print(f"Server started on {self.ip}:{self.port}")
        self.soket.listen(5)
        self.connectionthread = th.Thread(name="connlistener",target=self.connectionListener)
        self.connectionthread.start()

    def startTread(self,thread:th.Thread):
        self.threadlist.append(thread)
        thread.start()

    def connectionListener(self):
        while not self.stopevent.is_set():
            try:
                print("Server : En attente de nouvelle connexion...")
                conn, addr = self.soket.accept()
                print("Server : Connecté à : ", addr)
                thread = th.Thread(target=self.connection, args=(conn,addr))
                thread.start()
            except Exception as e:
                if not self.stopevent.is_set():
                    print("Server : Erreur de connexion :",e)
            
    def connection(self,conn:socket.socket,ip):
        try:
            client = Client(conn,ip,self.lastpid,self)
            self.lastpid += 1
            packet : ServerBoundPseudoPacket = client.sendRecv(cb.ClientBoundIdPacket(client.id))[0]
            player = Player(packet.name,client)
            self.world.join_player(player)
            self.threadlist.append(client.thread)
            client.thread.start()
        except Exception as e:
            print("Server : Erreur creation", e)

    def broadcast(self,packet:cb.ClientBoundPacket,ignored:list[int] = []):
        for player in self.world.players.values():
            if player.client.id not in ignored:
                player.client.send(packet)
                print("broadcast : sent packet to player :",player.client.id)
    
    def stop(self):
        try :
            # DO NOT TUCHE PLEASE
            self.stopevent.set()
            self.world.stop()
            if self.soket:
                self.soket.shutdown(socket.SHUT_RDWR)
                self.soket.close()
            for thread in self.threadlist:
                if thread.is_alive():
                    thread.join(10)
            self.connectionthread.join(10)
            self.threadlist = []
            print("Server stopped")
        except Exception as e:
            print("Server : Erreur de fermeture :",e)

if __name__ == "__main__":
    data.server = Server()
    cmd = input("")
    while cmd != "stop" or cmd != "exit":
        cmd = input("")
        pass
    data.server.stop()