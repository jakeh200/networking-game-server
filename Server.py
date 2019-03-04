import socket, sys
import time
import Queue

payload = 2048
backlog = 2

class Client():
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.settimeout(20)
        try:
            self.sock.connect((ip, port))
        except socket.timeout:
            print('Timed out trying to connect.')

    def send(self, message):
        try:
            self.sock.sendall(message.encode())
        except socket.timeout:
            print('Timed out trying to send.')

    def close(self):
        self.sock.close()


class Server():
    """
    Server has 2 ports, each for different uses.
		port1 --> used for matchmaking
		port2 --> used for updating player position in game
    """

    def __init__(self, ip, match_port):
        self.match_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.match_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.match_sock.bind((ip, match_port))
        self.match_sock.listen(backlog)

        self.clients = Queue.Queue()
        self.matches = []

    # def receive_update(self):
    #     data = None
    #     self.client, address = self.update_sock.accept()
    #     return client, address
    #     data = self.client.recv(payload).decode()
    #     return data

    #receives connection from client that wants to join a match
    def receive(self):
    	self.client, addr = self.match_sock.accept()
        clients.put((client, addr))
        return client, addr
    	#matchmake()

    #check if at least 2 players in queue
    #matches first 2 clients in queue
    def matchmake(self):
    	matched = False
    	start = time.time()
        new_match = None

    	#try to match for 60 seconds
    	while(not matched or time.time() - start > 60):
	    	if(clients.qsize() >= 2):
                #take first 2 clients in queue and create a new Match object
	    		new_match = match(clients.get(), clients.get())
	    		matched = True
	    	else:
	    		time.sleep(0.5)

        #add the new Match object to matches list
        if(new_match not in self.matches):
            self.matches.append(new_match)

	    return new_match
 	
    def clear_clients(self):
        self.clients.queue.clear()

    def clear_matches(self):
        self.matches = []

    #players are (conn, addr) pairs
    def match(self, player1, player2):
        return Match.Match(player1, player2)

    def close(self):
        self.match_sock.close()

#Match holds the connection and addresses of 2 clients
class Match():
    #player is (conn, addr) pair
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def send_msg_player1(self, message):
        player1.first.send(message)

    def send_msg_player2(self, message):
        player2.first.send(message)

    def get_player1_addr(self):
        return player1.second

    def get_player2_addr(self):
        return player2.second

    def close(self):
        player1.first.close()
        player2.first.close()


def send(msg, client_ip, client_port):
    client = Client(client_ip, client_port)
    client.send(msg)
    client.close()


