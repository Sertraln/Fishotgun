from server.main import Server
from client import data
from client.main import start
import threading as th
import subprocess

if __name__ == "__main__":
    process = subprocess.Popen(["python3", "server/main.py"],capture_output=True)
    try:
        start()
    except SystemExit as e:
        process.send_signal(0)
        process.wait()