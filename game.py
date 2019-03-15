import pygame, random, sys, socket
import Server, time
from pythonping import ping


# Initialize pygame
pygame.init()

#####################################################################
## --- NEXT 4 LINES MUST BE MODIFIED TO MATCH ACTUAL SITUATION --- ##
host = socket.gethostname() 
ip = socket.gethostbyname(host)
MY_SERVER_HOST = '192.168.0.14'
MY_SERVER_PORT = 5000
MY_IP = '192.168.0.14'
MY_PORT = 0
OTHER_HOST = ''
OTHER_PORT = 0
#####################################################################

#Ping values
NUM_PLAYERS = 8
pings = [10, 50, 100, 200] * (NUM_PLAYERS // 8)
# Set colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set screen dimensions
screen_width = 852
screen_height = 480

# Set player and ball dimensions
player_side = 50
ball_side = 75

# Set goal dimensions
goal_width = 30
goal_height = 300

# Set initial positions of players
redx = 100
redy = screen_height//2
bluex = screen_width - 100
bluey = screen_height//2

class Player(pygame.sprite.Sprite):
	
	def __init__(self, pos, color):

		# Call the parent class (Sprite) constructor
		super().__init__()

		# Create the square that will be the player
		self.image = pygame.surface.Surface((player_side, player_side))
		self.rect = self.image.get_rect(center = pos)
		self.image.fill(color)
		self.color = color

	def move(self, dir):
		if dir == 'up' and self.rect.top > 0:
			self.rect.centery -= 10
		if dir == 'down' and self.rect.bottom < screen_height:
			self.rect.centery += 10
		if dir == 'left' and self.rect.left > 0:
			self.rect.centerx -= 10
		if dir == 'right' and self.rect.right < screen_width:
			self.rect.centerx += 10

	def make_data_package(self):
		package_id = 'p'
		datax = str(self.rect.centerx).rjust(4, '0')
		datay = str(self.rect.centery).rjust(4, '0')
		return package_id + datax + datay

class Ball(pygame.sprite.Sprite):
 
	def __init__(self):
 
		# Call the parent class (Sprite) constructor
		super().__init__()
 
		# Load the image
		self.image = pygame.image.load("ball.png").convert()
	 
		# Set our transparent color
		self.image.set_colorkey(BLACK)
 
		# Fetch the rectangle object that has the dimensions of the image
		# Update position by setting the values of rect.x and rect.y
		self.rect = self.image.get_rect()
		self.rect.x = screen_width//2 - ball_side//2
		self.rect.y = screen_height//2 - ball_side//2

	def make_data_package(self):
		package_id = 'b'
		datax = str(self.rect.centerx).rjust(4, '0')
		datay = str(self.rect.centery).rjust(4, '0')
		return package_id + datax + datay

class Goal(pygame.sprite.Sprite):
	
	def __init__(self, color, x, y):
 
		# Call the parent class (Sprite) constructor
		super().__init__()
 
		# Create an image of the block, and fill it with a color.
		# This could also be an image loaded from the disk.
		self.image = pygame.Surface([goal_width, goal_height])
		self.image.fill(color)
 
		# Fetch the rectangle object that has the dimensions of the image
		# Update position by setting the values of rect.x and rect.y
		self.rect = self.image.get_rect()
		self.rect.x = x - player_side//2
		self.rect.y = y - player_side//2

class Background(pygame.sprite.Sprite):
	def __init__(self, image_file, location):
		pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
		self.image = pygame.image.load(image_file)
		self.rect = self.image.get_rect()
		self.rect.left, self.rect.top = location

def reset_sprites(me, enemy, ball):
	if (me.color == RED):
		me.rect = me.image.get_rect(center = (redx, redy))
	else:
		me.rect = me.image.get_rect(center = (bluex, bluey))
	ball.rect.x = screen_width//2 - ball_side//2
	ball.rect.y = screen_height//2 - ball_side//2

def text_objects(text, font):
	textSurface = font.render(text, True, WHITE)
	return textSurface, textSurface.get_rect()

def message_display(text, gameDisplay, size, x, y):
	largeText = pygame.font.Font('freesansbold.ttf',size)
	TextSurf, TextRect = text_objects(text, largeText)
	TextRect.center = (x,y)
	gameDisplay.blit(TextSurf, TextRect)
	pygame.display.update()

def ip_value(ip):
	""" ip_value returns ip-string as integer """
	return int(''.join([x.rjust(3, '0') for x in ip.split('.')]))


def define_players_and_goals():
	if (MY_PORT > OTHER_PORT):
		me = Player((redx, redy), RED)
		me_goal = Goal(RED, 10, screen_height//2 - 125)
		enemy = Player((bluex, bluey), BLUE)
		enemy_goal = Goal(BLUE, screen_width + 10, screen_height//2 - 125)
	else:
		me = Player((bluex, bluey), BLUE)
		me_goal = Goal(BLUE, screen_width + 10, screen_height//2 - 125)
		enemy = Player((redx, redy), RED)
		enemy_goal = Goal(RED, 10, screen_height//2 - 125)
	return me, enemy, me_goal, enemy_goal

#looks for match for 60 seconds
def look_for_match():
	print("Looking for match...\n")
	data = 'n'
	match_found = False
	start = time.time()
	index = 0
	min_ping_index = 0
	min_ping = 100000
	min_ping_opponent = ''
	while(1): #time.time() - start < 60):
		print("before receiving IP")
		data = conn.receive()
		print("after receiving IP, which is " + data)
		if (data[0] == 'd'): # Server is done sending IP addresses of other clients to ping
			break
		elif (data[0] == 'n'):
			continue
		else: # Data received is an IP address of a potential opponent.
			#response_list = ping(data, size=40, count=5)
			#ping = response_list.rtt_avg_ms
			rand = random.randint(0, len(pings) - 1)
			ping = pings[rand]
			pings.remove(ping)
			print(str(index) + ") opponent: " + data + " ping: " + str(ping))
			if (ping < min_ping):
				print("new minimum")
				min_ping = ping
				min_ping_index = index
				min_ping_opponent = data
				match_found = True
		index = index + 1

	if (match_found):
		print("MATCH FOUND, sending index " + str(min_ping_index))
		#Server.send(str(min_ping_index).rjust(4, '0'), MY_SERVER_HOST, MY_SERVER_PORT)
		conn.send(str(min_ping_index).rjust(4, '0'))

	# Wait for confirmation of opponent
	response = conn.receive()
	print("RESPONSE FROM SERVER: " + response)
	return response

#######################################################################
####                           GAME SETUP                          ####
#######################################################################

# Create the play window
screen = pygame.display.set_mode((screen_width, screen_height))

# Fill the background with the waiting screen
screen.fill((34,139,34))
message_display("Chrome Soccer", screen, 60, screen_width//2, screen_height//2 - 50)
message_display("Waiting for opponent...", screen, 25, screen_width//2, screen_height//2)
init_ball = Ball()
init_ball.rect = init_ball.image.get_rect(center = (screen_width//2, screen_height//2 + 50))
s_list = pygame.sprite.Group()
s_list.add(init_ball)
s_list.draw(screen)
pygame.display.update()

# Set the field background
BackGround = Background('field.jpg', [0,0])
pygame.display.set_caption("Chrome Soccer")

# Set initial score
me_score = 0
enemy_score = 0

# Set initial velocities
player_vel = 10
ball_vel = 0

# ball_dir is u, d, r, l
ball_dir = 'u'

#######################################################################
####                     CONNECT TO SERVER                         ####
#######################################################################

conn = Server.Client(MY_SERVER_HOST, MY_SERVER_PORT)

data = look_for_match()
#match was not found
if(data[0] == 'A'):
	print(data)
else:
	ip_and_port = data.split()
	OTHER_HOST = ip_and_port[3]
	OTHER_PORT = int(ip_and_port[4])
	MY_PORT = int(ip_and_port[5])

#close connection with server and bind self to MY IP and MY PORT to talk to opponent
conn.close()
print("Binding to ip: " + MY_IP + " on port: " + str(MY_PORT))
server = Server.Server(MY_IP, MY_PORT)

# Define the players, goals, and ball
me, enemy, me_goal, enemy_goal = define_players_and_goals()
ball = Ball()
all_sprites_list = pygame.sprite.Group()
all_sprites_list.add(me)
all_sprites_list.add(enemy)
all_sprites_list.add(ball)
all_sprites_list.add(me_goal)
all_sprites_list.add(enemy_goal)

# server = connection.Server(MY_SERVER_HOST, MY_SERVER_PORT)
print("Checking connection with opponent.\n")
connected = False
while(not connected):
	if(MY_PORT > OTHER_PORT):
		msg = server.receive_update()
		print(msg)
		connected = True
	else:
		try:
			#print("Sent check")
			Server.send("check", OTHER_HOST, OTHER_PORT)
			connected = True
		except socket.error:
			time.sleep(1)



#######################################################################
####                       MAIN GAME LOOP                          ####
#######################################################################
	
while True:

	# If they pressed the 'X' close the game
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			#server.shutdown()
			pygame.quit()
			sys.exit()

	# Get the key pressed
	keys = pygame.key.get_pressed()

	# Move the player
	for button, direction in [(pygame.K_UP, 'up'), (pygame.K_DOWN, 'down'),
							  (pygame.K_LEFT, 'left'), (pygame.K_RIGHT, 'right')]:
		if keys[button]:
			me.move(direction)

	# Check if either player hit the ball
	me_hit_ball = pygame.sprite.collide_rect(me, ball)
	enemy_hit_ball = pygame.sprite.collide_rect(enemy, ball)
	
	# If a player hit the ball, move it accordingly
	player_x = 0
	player_y = 0
	if (me_hit_ball):
		player_x = me.rect.x
		player_y = me.rect.y
	elif (enemy_hit_ball):
		player_x = enemy.rect.x
		player_y = enemy.rect.y
	if (me_hit_ball or enemy_hit_ball):
		ball_vel = 15
		xdiff = abs(player_x - ball.rect.x)
		ydiff = abs(player_y - ball.rect.y)
		if (xdiff > ydiff): # The ball is being hit along the x axis
			if (player_x < ball.rect.x): # Move ball to the right
				ball_dir = 'r'
			else:   # Move ball to the left
				ball_dir = 'l'
		else: # The ball is being hit along the y axis
			if (player_y < ball.rect.y): # Move the ball down
				ball_dir = 'd'
			else:   # Move the ball up
				ball_dir = 'u'

	# change the ball's direction if it hit a wall
	if (ball.rect.x < 5):
		ball_dir = 'r'
	if (ball.rect.y < 5):
		ball_dir = 'd'
	if (ball.rect.x > screen_width - ball_side):
		ball_dir = 'l'
	if (ball.rect.y > screen_height - ball_side):
		ball_dir = 'u'

	# change the ball's direction if it gets too close to the center of a player
	xdiff_me = abs(me.rect.x - ball.rect.x)
	xdiff_enemy = abs(enemy.rect.x - ball.rect.x)
	ydiff_me = abs(me.rect.y - ball.rect.y)
	ydiff_enemy = abs(enemy.rect.y - ball.rect.y)
	if ((xdiff_me < 40 and ydiff_me < 40) or (xdiff_enemy < 40 and ydiff_enemy < 40)):
		k = random.randint(0,1)
		if (k == 0):
			ball_dir = 'u'
		else:
			ball_dir = 'd'

	# Check if the ball hit either goal
	me_goal_made = pygame.sprite.collide_rect(ball, me_goal)
	enemy_goal_made = pygame.sprite.collide_rect(ball, enemy_goal)

	if (me_goal_made or enemy_goal_made):
		reset_sprites(me, enemy, ball)
		ball_vel = 0
		message_display("Goal!", screen, 115, screen_width/2, screen_height/2)
		pygame.time.delay(2000)
	if (me_goal_made):
		enemy_score = enemy_score + 1
	if (enemy_goal_made):
		me_score = me_score + 1

	# Send my position to the enemy
	me_data = me.make_data_package()
	Server.send(me_data, OTHER_HOST, OTHER_PORT)

	# Receive the enemy's position
	enemy_data = server.receive_update()
	package_id = enemy_data[0]
	if (package_id == 'p'): # Should be the enemy's position
		enemy.rect.centerx = int(enemy_data[1:5])
		enemy.rect.centery = int(enemy_data[5:])
	elif (package_id == 'b'): # Might be the ball's position
		ball.rect.centerx = int(enemy_data[1:5])
		ball.rect.centery = int(enemy_data[5:])

	# If RED player, calculate ball's new position and send it to the enemy
	if (me.color == RED):

		# Calculate ball's new position
		new_y_d = ball.rect.y + ball_vel
		new_y_u = ball.rect.y - ball_vel
		new_x_r = ball.rect.x + ball_vel
		new_x_l = ball.rect.x - ball_vel
		if (ball_dir == 'd' and new_y_d < screen_height - ball_side):
			ball.rect.y = new_y_d
		elif (ball_dir == 'u' and new_y_u > 0):
			ball.rect.y = new_y_u
		elif (ball_dir == 'r' and new_x_r < screen_width - ball_side):
			ball.rect.x = new_x_r
		elif (ball_dir == 'l' and new_x_l > 0):
			ball.rect.x = new_x_l
		if (ball_vel > 0):
			ball_vel -= 1
			
		# Send it to the enemy
		ball_data = ball.make_data_package()
		Server.send(ball_data, OTHER_HOST, OTHER_PORT)

	# If BLUE player, receive the ball's new position from the enemy
	else:
		ball_data = server.receive_update()
		package_id = ball_data[0]
		if (package_id == 'b'): # Should be the ball's position
			ball.rect.centerx = int(ball_data[1:5])
			ball.rect.centery = int(ball_data[5:])
		elif (package_id == 'p'): # Might be the enemy's position
			enemy.rect.centerx = int(ball_data[1:5])
			enemy.rect.centery = int(ball_data[5:])

	# Fill the background
	screen.fill((0,0,0))
	screen.blit(BackGround.image, BackGround.rect)

	# Draw all the sprites, re-draw the goals, re-draw the score, and update the screen
	all_sprites_list.draw(screen)
	pygame.draw.rect(screen, RED, (-20, screen_height//2 - 150, 60, 300))
	pygame.draw.rect(screen, BLUE, (screen_width - 40, screen_height//2 - 150, 60, 300))
	if (me.color == RED):
		message_display(str(me_score) + " - " + str(enemy_score), screen, 30, screen_width/2, 20)
	else:
		message_display(str(enemy_score) + " - " + str(me_score), screen, 30, screen_width/2, 20)
	pygame.display.flip()
	pygame.display.update()

	if (enemy_score == 5):
		message_display("You Lose!", screen, 115, screen_width/2, screen_height/2)
		pygame.time.delay(2000)
		break
	if (me_score == 5):
		message_display("You Win!", screen, 115, screen_width/2, screen_height/2)
		pygame.time.delay(2000)
		break

pygame.quit()
