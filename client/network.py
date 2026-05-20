import socket
import threading as th
import traceback
from client.packet.serverbound import ServerBoundPseudoPacket
from client.packet.packetstruct import ServerBoundPacket 
import client.data as data
import client.world as world
from shared.packetlib import UncompletePacketException

class Network:
    def __init__(self, ip, port,name):
        self.name = name
        from client.packet import packetlib
        packetlib.init_packetlib()
        print("server bound packets :",packetlib.packetlist.serverBoundPacketList)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ip
        self.stop_event = th.Event()
        self.port = port
        self.addr = (self.server, self.port)
        self.id = self.connect()
        print("client : id : "+str(self.id))
        self.thread = th.Thread(name="clientpacketlistner",target=self.packetListener)
        self.thread.daemon = True
        self.thread.start()
        self.send(ServerBoundPseudoPacket(name))
        self.buffer = b""

    def connect(self) -> Exception | int:
        print("client : Connexion à "+self.server)
        try:
            self.conn.settimeout(10)  # 10 second timeout
            self.conn.connect(self.addr)
            self.conn.settimeout(None)  # Reset to blocking mode
            print("client : Connexion réussie")
            recv = self.conn.recv(2048)
            if not recv:
                raise ConnectionError("Aucune donnée reçue du serveur")
            return recv[0]
        except socket.timeout:
            print("client : Timeout de connexion")
            raise ConnectionRefusedError("Timeout de connexion")
        except ConnectionRefusedError as e:
            print("client : Connexion refusée :",str(e))
            raise ConnectionError("Connexion refusée")
        except Exception as e:
            print("client : Erreur de connexion inconue:", str(e))
            raise ConnectionError("Erreur de connexion inconnue")
    
    def packetListener(self):
        from client.packet.packetlib import getClientBoundPacket
        while not self.stop_event.is_set():
            try:
                data = self.conn.recv(2048)
                if not data:
                    self.disconnect()
                    break
                data = self.buffer + data
                packets, self.buffer = getClientBoundPacket(data)
                for packet in packets:
                    try:
                        packet.handle()
                    except Exception as e:
                        print("client : Erreur de traitement du paquet :", repr(e))
                        print("client : packet type :", type(packet).__name__)
                        print("client : packet data :", getattr(packet, "data", None))
                        print(traceback.format_exc())
            except socket.timeout as e :
                print("client : Timeout de réception de paquet", e)
                self.disconnect()
                break
            except Exception as e:
                print("client : Erreur de réception de paquet", e)
                if data :
                    print("client : data :",data)
            

    def send(self, packet:ServerBoundPacket):
        if self.conn.fileno() == -1:
            return
        packet.send(self.conn)

    def sendRecv(self, data):
        self.send(data)
        return self.conn.recv(2048)

    def disconnect(self, trigger_quit_to_menu: bool = True):
        self.stop_event.set()
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except:
            pass
        current_thread = th.current_thread()
        if self.thread and self.thread.is_alive() and self.thread != current_thread:
            self.thread.join(timeout=3.0)
        print("client : Déconnexion")
        data.network = None
        if trigger_quit_to_menu:
            world.quit_to_menu()



def is_valid_ip(ip_str):
    parts = ip_str.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or not 0 <= int(part) <= 255:
            return False
    return True

def is_port(num_str):
    return num_str.isdigit() and 0 <= int(num_str) <= 65535
