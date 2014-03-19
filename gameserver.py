#!/usr/bin/python
import socket, time, threading, cPickle, pygame, sys, copy
from operator import sub,mul,add,div
from pygame.locals import *
BUFFER_SIZE = 1024

def main():
	connsocket = socket.socket()
	host = ''
	port = 8888
	connsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	connsocket.bind((host,port))
	connsocket.listen(5)
	
	while True:
		isock1, ip1 = connsocket.accept()
		#isock2, ip2 = connsocket.accept()
		tr = threading.Thread(target=instance, args = (isock1, ip1))#, isock2, ip2))
		tr.daemon = True
		tr.start()
	
def instance(sock1, ip1):#, sock2, ip2):
	while True:
		msg = sock1.recv(BUFFER_SIZE)
		if msg != '':
			reborn = cPickle.loads(msg)
			print reborn
		time.sleep(0.033333)

		
def superrecv(sock, addr):
	while True:
		message = sock.recv(BUFFER_SIZE)
		if message == '':
			break
		print message
		
main()
