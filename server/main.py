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
import signal

def get_local_ip():
    """
    Retourne l'adresse IP locale de la machine.
    """
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
            # if e.errno == socket.errno.EADDRINUSE:
            #     print(f"Port {self.port} is already in use. Trying another port...")
            #     self.__init__(port=self.port+1, ip=self.ip)
            #     return
            print("server :error binding :",e)
            raise e
        print(f"Server started on {self.ip}:{self.port}")
        self.soket.listen(5)
        self.connectionthread = th.Thread(name="connlistener",target=self.connectionListener)
        self.connectionthread.start()
        data.server = self

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
            player = Player(packet.name,client,self.world.world_scene)
            self.world.join_player(player)
            self.threadlist.append(client.thread)
            client.thread.start()
        except Exception as e:
            print("Server : Erreur creation", e)

    def broadcast(self,packet:cb.ClientBoundPacket,ignored:list[int] = []):
        """
        Send a packet to all connected players except those in ignored list
        """
        for player in self.world.players.values():
            if player.client.id not in ignored:
                player.client.send(packet)
                print("broadcast : sent packet to player :",player.client.id)
    
    def stop(self):
        try:
            data.server.world.save()
        except Exception as e:
            print("Server : Erreur de sauvegarde :",e)
        try :
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
            raise SystemExit(0)
        except Exception as e:
            print("Server : Erreur de fermeture :",e)

if __name__ == "__main__":
    server = Server()
    signal.signal(signal.SIGINT, lambda sig, frame: server.stop())
    cmd = input("")
    while cmd != "stop" and cmd != "exit":
        cmd = input("")
    server.stop()