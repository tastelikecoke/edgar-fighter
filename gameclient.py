#!/usr/bin/python
import socket, time, threading, cPickle, sys, copy
from gamemodules import *
def main():
	cmdsock = socket.socket()
	updsock = socket.socket()
	host = '127.0.0.1'
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
	ball = pygame.image.load('ball.png')
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
	player1 = Entity(w=entli[0], s=entli[1])
	player2 = Entity(w=entli[2], s=entli[3])
	floor = Entity(w=entli[4], s=entli[5])
	wall1 = Entity(w=entli[6], s=entli[7])
	wall2 = Entity(w=entli[8], s=entli[9])
	sf.make(player1,ball)
	sf.make(player2,ball)
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
		try:
			entitylist = cPickle.loads(stri)
		finally:
			pass
		player1.w, player1.s, player2.w, player2.s, player1.a, player2.a = entitylist
def appendhelper(keytype,id,mode):
	stri = id
	if keytype == K_a:
		stri = stri+'a'
	elif keytype == K_d:
		stri = stri+'d'
	elif keytype == K_w:
		stri = stri+'w'
	else:
		stri = stri+'s'
	if mode == KEYUP:
		stri = stri+'U'
	else:
		stri = stri+'D'
	return stri

main()
