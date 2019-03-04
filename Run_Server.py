import thread
import Server
import time
import sys
import socket

MY_SERVER_HOST = '169.231.75.20'
MY_SERVER_PORT = 5000

#this is run when a client wants to join a match
def create_match(conn, addr):
    match = server.matchmake()
    if(match != None):
    	# conn.send("Found a match.\n")
    	player1 = match.get_player1_addr()
    	player2 = match.get_player2_addr()

    	#if i'm player1, send address of player2, else send addr of player1
    	if(player1 == addr):
			conn.send(player2)
		else:
			conn.send(player1)
    else:
    	conn.send("A match could not be found. Please try again.\n")

    conn.close()
    # print(match.get_player1_addr())

def run():
	#initialize server
	server = Server.Server(MY_SERVER_HOST, MY_SERVER_PORT)
	print("Server is running.\n")

	while True:
	   # Establish connection with client.
	   c, addr = server.receive()   
	   print("Established connection with client", c, "at addr", addr)
	   thread.start_new_thread(create_match,(c,addr))

run()

