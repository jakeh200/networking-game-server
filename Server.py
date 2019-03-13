import socket, sys
import time
import queue, threading
from pythonping import ping

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
	def matchmake(self, addr):
		#check if a match has been found for this address
		for match in self.matches:
			if(addr == match.get_player1_addr() or addr == match.get_player2_addr()):
				return match

		matched = False
		start = time.time()
		new_match = None

		#try to match for 60 seconds
		while(not matched and time.time() - start < 20):
			print("Time since start", time.time() - start)
			if(self.client_queue.qsize() >= 2):
				# Ping all of the clients in the queue
				# Match up the player with the quickest ping and the player with the slowest ping
				max_ping = 0
				min_ping = 100000
				max_ping_player = None
				min_ping_player = None
				for player in self.clients:
					ip_addr = player[1][0]
					response_list = ping(ip_addr, size = 40, count = 5)
					p = response_list.rtt_avg_ms
					print("current player: " + ip_addr + " " + str(player[1][1]) + " ping: " + str(p))
					if (p > max_ping):
						print("NEW MAX")
						max_ping = p
						max_ping_player = player
					if (p <= min_ping):
						print("NEW MIN")
						min_ping = p
						min_ping_player = player
				print("max_ping_player: " + max_ping_player[1][0] + " " + str(max_ping_player[1][1]))
				print("min_ping_player: " + min_ping_player[1][0] + " " + str(min_ping_player[1][1]))
							      
				# Match the player with quickest ping with player with slowest ping
				if (max_ping_player != min_ping_player):
					new_match = self.match(max_ping_player, min_ping_player)
					self.clients.remove(max_ping_player)
					self.clients.remove(min_ping_player)
					matched = True
			else:
				time.sleep(5)

		#add the new Match object to matches list
		if(new_match not in self.matches and new_match != None):
			self.matches.append(new_match)

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


