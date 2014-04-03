#!/usr/bin/python
import socket, time, threading, cPickle, sys, copy
from gamemodules import *
superflag = False
def main():
	pygame.init()
	surf = pygame.display.set_mode((640,480))
	pygame.display.set_caption("Game")
	fps = pygame.time.Clock()
	cmdsock = socket.socket()
	updsock = socket.socket()
	host = 'localhost'
	port = 8888
	id = ""
	
	waiting = 0
	comicsans = pygame.font.SysFont("Comic Sans MS",12)
	while waiting != 2:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
		if waiting == 0:
			words = comicsans.render("Connecting to "+host+":"+str(port)+" waiting for others",1,black)
			try:
				cmdsock.connect((host,port))
				updsock.connect((host,port))
				waiting += 1
			except Exception as e:
				words = comicsans.render("error"+str(e),1,black)
				pass
		elif waiting == 1:
			id = cmdsock.recv(BUFFER_SIZE)
			waiting += 1
		surf.fill(white)
		surf.blit(words, (10,10))
		pygame.display.update()
	
	
	updateThread = threading.Thread(target=Update, args=(updsock,id,surf))
	updateThread.start()
	# [INPUT] get keyboard inputs
	while True:
		inputs = []
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				cmdsock.send('closejemprotocolv2')
				pygame.quit()
				sys.exit()
			if not superflag and event.type == KEYDOWN or event.type == KEYUP:
				inputs.append(appendhelper(event.key,id,event.type))
		if not superflag and len(inputs) > 0:
			packet = cPickle.dumps(inputs)
			packet += "jemprotocolv2"
			numBytes = cmdsock.send(packet)
		fps.tick(60)
def Update(socket,id,surf):
	global superflag
	comicsans = pygame.font.SysFont("Comic Sans MS",12)
	# [UPDATE] get screen updates from server
	fps = pygame.time.Clock()
	#ball = pygame.image.load('ball.png')
	swordiemoves = {
		#state animations here (numbering might be confusing for states and animations)
		0:[], #Standing
		1:[], #Lateral movement
		2:[], #Crouch
		3:[], #Getting hit
		4:[], #Attack (slash)
		5:[], #Attack (crouch slash)
		6:[], #Block (block)
		7:[], #Block (crouch block)
		9:[], #Die
	}
	swordiemoves[0].append(pygame.image.load('./Swordsman/Stand/1.png'))
	for i in range(7):
		stri = './Swordsman/Forward and Backward/'+str(i+1)+'.png'
		swordiemoves[1].append(pygame.image.load(stri))
		swordiemoves[1].append(pygame.image.load(stri))
		swordiemoves[1].append(pygame.image.load(stri))
	swordiemoves[2].append(pygame.image.load('./Swordsman/Crouch/Idle/1.png'))
	for i in range(4):
		stri = './Swordsman/Hit/'+str(i+1)+'.png'
		swordiemoves[3].append(pygame.image.load(stri))
		swordiemoves[3].append(pygame.image.load(stri))
	for i in range(13):
		stri = './Swordsman/Ground Attack/Slash/'+str(i+1)+'.png'
		swordiemoves[4].append(pygame.image.load(stri))
	for i in range(11):
		stri = './Swordsman/Ground Attack/Down Slash/'+str(i+1)+'.png'
		swordiemoves[5].append(pygame.image.load(stri))
	swordiemoves[6].append(pygame.image.load('./Swordsman/Ground Attack/Block/1.png'))
	swordiemoves[7].append(pygame.image.load('./Swordsman/Crouch/Block/1.png'))
	swordiemoves[9].append(pygame.image.load('./Swordsman/Die/1.png'))
	
	bg = pygame.image.load('bg.png')
	sf = SpriteFactory(surf,[320,240],specials=[bg])
	#initial entity dumps
	buffer = ""
	while True:
		temp = socket.recv(BUFFER_SIZE)
		buffer += temp
		if len(temp) < BUFFER_SIZE:
			break
	packedInitState = buffer.split('jemprotocolv2')[0]
	buffer = buffer[len(packedInitState+'jemprotocolv2'):]
	initState = cPickle.loads(packedInitState)
	
	player1 = Entity(1,w=initState[0], s=initState[1], health=initState[10])
	player2 = Entity(2,w=initState[2], s=initState[3], health=initState[11])
	floor = Entity(w=initState[4], s=initState[5])
	wall1 = Entity(w=initState[6], s=initState[7])
	wall2 = Entity(w=initState[8], s=initState[9])
	sf.make(player1,swordiemoves)
	sf.make(player2,swordiemoves)
	sf.make(floor)
	sf.make(wall1)
	sf.make(wall2)
	
	buffer = ""
	while True:
		surf.fill(white)
		if not superflag:
			sf.draw()
			pygame.display.update()
			while len(buffer) < BUFFER_SIZE:
				temp = socket.recv(BUFFER_SIZE)
				buffer += temp
			state = []
			states = buffer.split('jemprotocolv2')
			packedState = states[-2]
			if packedState == 'win' or packedState == 'lose':
				superflag = True
				time.sleep(2)
		if superflag:
			words = comicsans.render('You '+packedState+'!',1,black)
			surf.blit(words, (10,10))
			pygame.display.update()
			fps.tick(60)
		else:
			buffer = buffer[len(buffer)-len(states[-1]):]
			state = cPickle.loads(packedState)
			player1.w = state[0]
			player1.s = state[1]
			player2.w = state[2]
			player2.s = state[3]
			player1.a = state[4]
			player2.a = state[5]
			player1.health = state[6]
			player2.health = state[7]
def appendhelper(keytype,id,mode):
	stri = id
	if keytype == K_a:
		stri = stri+'a'
	elif keytype == K_d:
		stri = stri+'d'
	elif keytype == K_w:
		stri = stri+'w'
	elif keytype == K_j:
		stri = stri+'j'
	elif keytype == K_k:
		stri = stri+'k'
	elif keytype == K_s:
		stri = stri+'s'
	else:
		stri = stri+'`'
	if mode == KEYUP:
		stri = stri+'U'
	else:
		stri = stri+'D'
	return stri

main()
