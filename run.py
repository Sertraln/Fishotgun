from server.main import Server
from client import data
from client.main import start
import threading as th

if __name__ == "__main__":
    server = Server()
    start(server.ip, server.port, "Player1")
    server.stop()