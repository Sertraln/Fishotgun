from ursina.networking import *
from player import Player

rpc_peer = RPCPeer()

map_connections = {}
next_player_id = 1

@rpc(rpc_peer)
def on_connect(connection:Connection, time_connected):
	print("This is run when a connect happens.")
	map_connections[connection.uid] = Player(next_player_id)
	global next_player_id
	next_player_id += 1

@rpc(rpc_peer)
def on_disconnect(connection: Connection, time_disconnected):
	print("This is run when a disconnect happens.")

@rpc(rpc_peer)
def initialise_player(connection: Connection, time_received, name: str):
	player = map_connections.get(connection.uid)
	if player:
		player.initialise(name)
		print(f"Player {player.player_id} initialised with name: {name}")

@rpc(rpc_peer)
def position(connection: Connection, time_received, position: Vec3):
	player = map_connections.get(connection.uid)
	if player and player.initialised:
		print(f"Received position {position} from player {player.player_id}")

def update():
	# Handle networking events, run this every update.
	rpc_peer.update()

rpc_peer.start("localhost", 8080, is_host=True)
print("Server started, waiting for connections...")

while rpc_peer.is_running():
	rpc_peer.update()