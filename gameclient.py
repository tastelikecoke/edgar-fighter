#!/usr/bin/python
import socket, time, threading, cPickle, sys, copy
from gamemodules import *
def main():
	cmdsock = socket.socket()
	updsock = socket.socket()
	host = 'localhost'
	port = 8888
	cmdsock.connect((host,port))
	updsock.connect((host,port))
	id = cmdsock.recv(BUFFER_SIZE)
	
	pygame.init()
	surf = pygame.display.set_mode((640,480))
	pygame.display.set_caption("Game")
	fps = pygame.time.Clock()
	tr = threading.Thread(target=Update, args=(updsock,id,surf))
	tr.start()
	# [INPUT] get keyboard inputs
	while True:
		li = []
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN or event.type == KEYUP:
				li.append(appendhelper(event.key,id,event.type))
		if len(li) > 0:
			stri = cPickle.dumps(li)
			numBytes = cmdsock.send(stri)
		fps.tick(60)
	
def Update(socket,id,surf):
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
		7:[], #Block
	}
	swordiemoves[0].append(pygame.image.load('../edgar-fighter/Swordsman/Stand/1.png'))
	for i in range(7):
		stri = '../edgar-fighter/Swordsman/Forward and Backward/'+str(i+1)+'.png'
		swordiemoves[1].append(pygame.image.load(stri))
		swordiemoves[1].append(pygame.image.load(stri))
		swordiemoves[1].append(pygame.image.load(stri))
	swordiemoves[2].append(pygame.image.load('../edgar-fighter/Swordsman/Crouch/1.png'))
	for i in range(4):
		stri = '../edgar-fighter/Swordsman/Hit/'+str(i+1)+'.png'
		swordiemoves[3].append(pygame.image.load(stri))
		swordiemoves[3].append(pygame.image.load(stri))
	for i in range(13):
		stri = '../edgar-fighter/Swordsman/Ground Attack/Slash/'+str(i+1)+'.png'
		swordiemoves[4].append(pygame.image.load(stri))
	for i in range(11):
		stri = '../edgar-fighter/Swordsman/Ground Attack/Down Slash/'+str(i+1)+'.png'
		swordiemoves[5].append(pygame.image.load(stri))
	swordiemoves[7].append(pygame.image.load('../edgar-fighter/Swordsman/Ground Attack/Block/1.png'))
	bg = pygame.image.load('bg.png')
	sf = SpriteFactory(surf,[320,240],specials=[bg])
	#initial entity dumps
	entstr = ''
	while True:
		temp = socket.recv(BUFFER_SIZE)
		entstr += temp
		if len(temp) < BUFFER_SIZE:
			break
	entli = cPickle.loads(entstr)
	player1 = Entity(1,w=entli[0], s=entli[1], health=entli[10])
	player2 = Entity(2,w=entli[2], s=entli[3], health=entli[11])
	floor = Entity(w=entli[4], s=entli[5])
	wall1 = Entity(w=entli[6], s=entli[7])
	wall2 = Entity(w=entli[8], s=entli[9])
	sf.make(player1,swordiemoves)
	sf.make(player2,swordiemoves)
	sf.make(floor)
	sf.make(wall1)
	sf.make(wall2)
	
	while True:
		surf.fill(white)
		sf.draw()
		pygame.display.update()
		stri = ''
		while True:
			temp = socket.recv(BUFFER_SIZE)
			stri += temp
			if len(temp) < BUFFER_SIZE:
				break
		entitylist = []
		try:
			s = stri.split('\n')
			for i in range(0,6):
				s[i] = s[i].split(' ')
				entitylist.append([])
				for j in s[i][:-1]:
					if i == 4 or i == 5:
						entitylist[i].append(int(j))
					else:
						entitylist[i].append(float(j))
			entitylist.append(float(s[6]))
			entitylist.append(float(s[7]))
		finally:
			pass
		print entitylist
		player1.w = entitylist[0]
		player1.s = entitylist[1]
		player2.w = entitylist[2]
		player2.s = entitylist[3]
		magic1 = entitylist[4]
		magic2 = entitylist[5]
		player1.health = entitylist[6]
		player2.health = entitylist[7]
		
		player1.a['state'] = magic1[0]
		player1.a['time'] = magic1[1]
		
		player2.a['state'] = magic2[0]
		player2.a['time'] = magic2[1]
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
	else:
		stri = stri+'s'
	if mode == KEYUP:
		stri = stri+'U'
	else:
		stri = stri+'D'
	return stri

main()
