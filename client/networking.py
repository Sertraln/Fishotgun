from ursina.networking import *
from data import player
from player import get_player
rpc_peer = RPCPeer()

@rpc(rpc_peer)
def on_connect(connection, time_connected):
	print("This is run when a new connection is established.")
	if rpc_peer.is_hosting():
		print("This is only run if we are the host (the server).")

@rpc(rpc_peer)
def on_disconnect(connection, time_disconnected):
	print("This is run when a disconnect happens.")

@rpc(rpc_peer)
def initialise_player(connection, time_received, name: str):
	pass

@rpc(rpc_peer)
def position(connection: Connection, time_received, position: Vec3):
	pass

@rpc(rpc_peer)
def update_position(connection: Connection, time_received,id:int, position: Vec3):
	#todo
	player = get_player(id)
	player.world_position = position

@rpc(rpc_peer)
def init_id(connection: Connection, time_received, id: int):
	player.set_id(id)

def update():
	# Handle networking events, run this every update.
	rpc_peer.update()


def start():
	rpc_peer.start("localhost", 8080, is_host=False)