#!/usr/bin/python
import socket, time, threading, cPickle, pygame, sys, copy
from operator import sub,mul,add,div
from pygame.locals import *

white = pygame.Color(255,255,255)
black = pygame.Color(0,0,0)
BUFFER_SIZE = 1024

def main():
	sock = socket.socket()
	host = '127.0.0.1'
	port = 8888
	sock.connect((host,port))
	
	tr = threading.Thread(target=getpresses, args=(sock,))
	tr.start()
	#while True:
	#	msg = sock.recv(BUFFER_SIZE)
	#	print msg
	#	fps.tick(60)
	
def getpresses(socket):
	pygame.init()
	surf = pygame.display.set_mode((640,480))
	fps = pygame.time.Clock()
	dic = {
		K_a: (lambda: li.append('a')),
		K_d: (lambda: li.append('d')),
		K_w: (lambda: li.append('w')),
		K_s: (lambda: li.append('s')),
	}
	while True:
		li = []
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN or event.type == KEYUP:
				try:
					dic[event.key]()
				except KeyError:
					pass
		if len(li) > 1:
			stri = cPickle.dumps(li)
			print li
			numBytes = socket.send(stri)
		fps.tick(30)
main()
