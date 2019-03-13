import socket, sys
import time
import queue, threading

payload = 2048
backlog = 2

class Client():
	def __init__(self, ip, port):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.sock.settimeout(20)
		try:
			self.sock.connect((ip, port))
		except socket.error:
			print('There was an error trying to connect.\n')

	def receive(self):
		data = None
		try:
			data = self.sock.recv(payload).decode()
		except socket.error:
			return None
		return data

	def send(self, message):
		try:
			self.sock.sendall(message.encode())
		except socket.timeout:
			print('Timed out trying to send.\,')

	def close(self):
		self.sock.close()


class Server():

	def __init__(self, ip, match_port):
		self.match_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.match_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.match_sock.bind((ip, match_port))
		self.match_sock.listen(backlog)
		#clients is list of ip address, port tuples
		self.lock = threading.Lock()
		self.client_queue = queue.Queue()
		self.clients = []
		self.matches = []

	def receive_update(self):
	    data = None
	    self.client, address = self.match_sock.accept()
	    data = self.client.recv(payload).decode()
	    return data

	#receives connection from client that wants to join a match
	def receive_conn(self):
		client, addr = self.match_sock.accept()
		self.lock.acquire()
		self.client_queue.put((client, addr))
		self.clients.append((client, addr))
		self.lock.release()
		return client, addr
		#matchmake()

	#check if at least 2 players in queue
	#matches first 2 clients in queue
	#Will never be called by more than 1 thread at a time
	def matchmake(self, addr, conn):
		print("matchmaking...")
		#check if a match has been found for this address
		for match in self.matches:
			if(addr == match.get_player1_addr() or addr == match.get_player2_addr()):
				print("previous match found")
				d = "done"
				conn.send(d.encode())
				return match

		matched = False
		start = time.time()
		new_match = None

		#try to match for 60 seconds
		while(not matched and time.time() - start < 20):
			print("Time since start", time.time() - start)
			if(len(self.clients) >= 2):
				# Send the first client the list of the rest of the clients
				player1 = self.clients.pop(0)
				player1_ip = player1[1][0]
				player1_port = player1[1][0]
				print("player 1 IP: " + player1_ip + " and port: " + str(player1_port))
				for opponent in self.clients:
					opponent_ip = opponent[1][0]
					print("sending opponent " + opponent_ip)
					conn.send(opponent_ip.encode())
				d = "done"
				print(d)
				conn.send(d.encode())

				# Recieve the index of the opponent chosen by the player based on pings
				data = conn.recv(payload).decode()
				player2_index = int(data)
				player2 = self.clients.pop(player2_index)
				print(str(player2_index) + ") player chosen, IP: " + player2[1][0] + " port: " + str(player2[1][1]))
				
				# Take these two clients and create a new Match object
				new_match = self.match(player1, player2)
				matched = True
			else:
				time.sleep(5)

		#add the new Match object to matches list
		if(new_match not in self.matches and new_match != None):
			self.matches.append(new_match)

		print("matchmaking done")
		return new_match
	
	def clear_clients(self):
		self.client_queue.queue.clear()

	def clear_matches(self):
		self.matches = []

	#players are (conn, addr) pairs
	def match(self, player1, player2):
		return Match(player1, player2)

	def close(self):
		self.match_sock.close()

#Match holds the connection and addresses of 2 clients
class Match():
	#player is (conn, addr) pair
	def __init__(self, player1, player2):
		self.player1 = player1
		self.player2 = player2

	def send_msg_player1(self, message):
		self.player1[0].send(message)

	def send_msg_player2(self, message):
		self.player2[0].send(message)

	def get_player1_addr(self):
		return self.player1[1]

	def get_player2_addr(self):
		return self.player2[1]

	def close(self):
		self.player1.first.close()
		self.player2.first.close()


def send(msg, client_ip, client_port):
	client = Client(client_ip, client_port)
	client.send(msg)
	client.close()


