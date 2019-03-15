import _thread, threading
import Server
import time
import sys
import socket

MY_SERVER_HOST = '169.231.75.45'
MY_SERVER_PORT = 5000

lock = threading.Lock()
server = None

#this is run when a client wants to join a match
def create_match(conn, addr):
	global server
	print("Finding match for", addr[0])
	
	lock.acquire()
	start = time.time()
	match = server.matchmake(addr)
	end = time.time()
	lock.release()

	time_to_match = end - start
	print("It took:", time_to_match, "seconds to find a match.")
	
	if(match != None):
		# conn.send("Found a match.\n")
		player1 = match.get_player1_addr()
		player2 = match.get_player2_addr()
		print("Found match with:", player1, "and", player2)

		#if i'm player1, send address of player2, else send addr of player1
		if(player1 == addr):
			print("Sending message to", addr)
			msg = "Found match with: " + player2[0] + " " + str(player2[1]) + " " + str(player1[1])
			conn.send(msg.encode())
		else:
			print("Sending message to", addr)
			msg = "Found match with: " + player1[0] + " " + str(player1[1]) + " " + str(player2[1])
			conn.send(msg.encode())
	else:
		msg = ("A match could not be found for " + addr[0])
		print(msg)
		conn.send(msg.encode())
		server.clear_clients()

	conn.close()
	
	# print(match.get_player1_addr())

def run():
	global server
	#initialize server
	server = Server.Server(MY_SERVER_HOST, MY_SERVER_PORT)
	print("Server is running.\n")

	while True:
	   # Establish connection with client.
	   c, addr = server.receive_conn()   
	   print("Established connection with client", addr[0])
	   _thread.start_new_thread(create_match,(c,addr))

run()

