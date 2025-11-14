from ursina.networking import RPCPeer
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
def say(connection, time_received, message: str):
	print(message)

def update():
	# Handle networking events, run this every update.
	rpc_peer.update()
	
rpc_peer.start("localhost", 8080, is_host=False)