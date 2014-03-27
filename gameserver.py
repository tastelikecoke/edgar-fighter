#!/usr/bin/python
import socket, time, threading, cPickle, sys, copy
from gamemodules import *

def main():
	connsocket = socket.socket()
	host = 'localhost'
	port = 8888
	connsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	connsocket.bind((host,port))
	connsocket.listen(5)
	
	# [MAIN SERVER THREAD] accepts connections from two players and makes a game instance (ideally should fork a process, pero threading muna)
	cmdsock1, ip1 = connsocket.accept()
	updsock1, ip1 = connsocket.accept()
	cmdsock2, ip2 = connsocket.accept()
	updsock2, ip2 = connsocket.accept()
	cmdsock1.send('1')
	cmdsock2.send('2')
	tr = threading.Thread(target=instance, args = (cmdsock1, cmdsock2, updsock1, updsock2, ip1, ip2))
	tr.daemon = True
	tr.start()
	while True:
		pass
	
def instance(cmdsock1, cmdsock2, updsock1, updsock2, ip1, ip2):
	# [INSTANCE] game instance between two players
	fps = pygame.time.Clock()
	# make all the factories
	pf = PhysicsFactory()
	# make all the entities
	player1 = Entity(1,w=[20.0,100.0],health=100.0)
	player2 = Entity(2,w=[20.0,100.0],s=[100.0,0.0],health=100.0)
	floor = Entity(w=[800.0,40.0], s=[0,100.0])
	wall1 = Entity(w=[140.0,600.0], s=[390.0,0.0])
	wall2 = Entity(w=[140.0,600.0], s=[-390.0,0.0])
	# make all the physics and sprites
	pf.make(player1,gravity=10.0,kind="player")
	pf.make(player2,gravity=10.0,kind="player")
	pf.make(floor,gravity=0.0,kind="floor")
	pf.make(wall1,gravity=0.0,kind="wall")
	pf.make(wall2,gravity=0.0,kind="wall")
	
	#initial state dump
	initState = [player1.w, player1.s, player2.w, player2.s, floor.w, floor.s, wall1.w, wall1.s, wall2.w, wall2.s, player1.health, player2.health]
	packedInitState = cPickle.dumps(initState)
	updsock1.send(packedInitState)
	updsock2.send(packedInitState)
	
	thread1 = threading.Thread(target=Input, args=(cmdsock1,ip1,player1,player2))
	thread2 = threading.Thread(target=Input, args=(cmdsock2,ip2,player2,player1))
	thread1.start()
	thread2.start()
	# [UPDATE] send state updates to players
	while True:
		pf.update()
		player1.updateAnimation()
		player2.updateAnimation()
		state = [player1.w, player1.s, player2.w, player2.s, player1.a.values(), player2.a.values(), player1.health, player2.health]
		string = ""
		for s in state[0:6]:
			if type(s) is list:
				for t in s:
					string += str(t)
					string += " "
			string += "\n"
		string += str(player1.health) +"\n" + str(player2.health)
		string += '\n*'
		packedState = string
		updsock1.send(packedState)
		updsock2.send(packedState)
		fps.tick(60)

def Input(sock, addr, player, opponent):
	# [INPUT] receive keyboard input from players
	buttonToggle = [False, False]
	downdic = {
			'a': (lambda: player.physics.push(-20.0)),
			'd': (lambda: player.physics.push(20.0)),
			'w': (lambda: player.physics.jump(-300.0)),
			'j': (lambda x: player.physics.attack(x)),
			's': player.physics.duck,
			'k': player.physics.block,
	}
	updic = {
			's': player.physics.unduck,
			'k': player.physics.block,
	}
	toggleThread = threading.Thread(target=Toggle, args=(player,buttonToggle))
	toggleThread.start()
	msg = ""
	while True:
		msg += sock.recv(BUFFER_SIZE)
		while msg != '':
			msgprime = msg.split('JEMPROTOCOL')[0]
			msg = msg[len(msgprime+'JEMPROTOCOL'):]
			reborn = cPickle.loads(msgprime)
			for press in reborn:
				if press[2] == 'U':
					try:
						if press[1] == 'a':
							buttonToggle[0] = False
						elif press[1] == 'd':
							buttonToggle[1] = False
						else:
							updic[press[1]]()
					except KeyError:
						pass
				elif press[2] == 'D':
					try:
						if press[1] == 'a':
							buttonToggle[0] = True
						elif press[1] == 'd':
							buttonToggle[1] = True
						elif press[1] == 'j':
							downdic[press[1]](opponent)
						else:
							downdic[press[1]]()
					except KeyError:
						pass

def Toggle(player, buttonToggle):
	fps = pygame.time.Clock()
	while True:
		if buttonToggle[0]:
			player.physics.push(-20.0)
		if buttonToggle[1]:
			player.physics.push(20.0)
		fps.tick(60)

main()
