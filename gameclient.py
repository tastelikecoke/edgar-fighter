#!/usr/bin/python
import socket, time, threading, cPickle, pygame, sys, copy
from operator import sub,mul,add,div
from pygame.locals import *

white = pygame.Color(255,255,255)
black = pygame.Color(0,0,0)
BUFFER_SIZE = 1024

def strictlygreater(a,b):
	"if a tuple is strictly greater than another tuple return true else false"
	return a[0] > b[0] and a[1] > b[1] 
def getCorners(e):
	"get the upper left corner and bottom right corner of an entity"
	corner1 = map(lambda x,y:x-y/2.0, e.s, e.w)
	corner2 = map(lambda x,y:x+y/2.0, e.s, e.w)
	return (corner1, corner2)
class Physics: # Physics is model
	def __init__(self,entity,kind,v,gravity):
		"a physics component has a parent entity, a kind (floor,wall or player),v (velocity), and gravity"
		self.entity = entity
		self.controlled = False
		self.onFloor = False
		self.kind = "floor" if kind == None else kind
		self.v = [0.0,0.0] if v == None else v
		self.gravity = 0.0 if gravity == None else gravity
		self.touchLeft = False #hack hack
	def update(self):
		"update the physics component of entity"
		self.v[1] += self.gravity
		originals = self.entity.s
		self.entity.s = map(add,self.entity.s, [v/30.0 for v in self.v])
		self.v[0] *= 0.70
		self.onFloor = False
	def push(self, speed):
		self.v[0] += speed
		self.controlled = True
	def jump(self, speed):
		if self.onFloor:
			self.v[1] += speed
			self.entity.s[1] -= 1
			self.controlled = True
	def duck(self):
		self.entity.w[1] = 60
		self.entity.s[1] += 20
	def unduck(self):
		self.entity.w[1] = 100
		self.entity.s[1] -= 20
	def resolve(self, jp):
		i = self.entity
		ip = self
		j = jp.entity
		i1,i2 = getCorners(i)
		j1,j2 = getCorners(j)
		if strictlygreater(i2,j1) and strictlygreater(j2,i1): # enter here if two bounding boxes collide
			if jp.kind == "floor": # enter here if target bounding box is a floor
				self.onFloor = True
				self.touchLeft = False #hack hack
				if j2[1] > i2[1]:
					i.s[1] = j.s[1] - (j.w[1] + i.w[1])/2
					ip.v[1] = 0
				else:
					i.s[1] = j.s[1] + (j.w[1] + i.w[1])/2
					ip.v[1] = 0
			else: # enter here if target bounding box is anything else
				if j2[0] > i2[0]:
					if jp.kind == "wall" and not self.onFloor: #hack hack
						self.touchLeft = True #hack hack
					i.s[0] = j.s[0] - (j.w[0] + i.w[0])/2
					ip.v[0] = 0
					jp.v[0] = 0
				else:
					i.s[0] = j.s[0] + (j.w[0] + i.w[0])/2
					ip.v[0] = 0
					jp.v[0] = 0				
				if self.touchLeft: #hack hack
					i.s[0] -= 1 #hack hack
class PhysicsFactory:
	def __init__(self):
		"a physics factory has backdrops and players"
		self.backdrops = []
		self.players = [] 
	def make(self,entity,v=None,gravity=None,kind=None):
		"makes a new physics component for an entity"
		p = Physics(entity,kind,v,gravity)
		entity.physics = p
		if kind == "player":
			self.players.append(p)
		else:
			self.backdrops.append(p)
		return p
	def update(self):
		"update all physics components"
		for i in range(2):
			p = self.players[i]
			q = self.players[(i+1)%2]
			p.update()
			for b in self.backdrops:
				p.resolve(b)
			if p.controlled == True:
				p.resolve(q)
		for p in self.players:
			p.controlled = not p.onFloor
class Sprite:
	def __init__(self,factory,entity,img=None):
		"a sprite has parent factory and parent entity"
		self.img = None if img == None else img
		self.factory = factory
		self.entity = entity
	def draw(self):
		"draws the sprite component of entity"
		corner1,corner2 = getCorners(self.entity)
		position = map(add,corner1,self.factory.origin)
		positionp = map(add,position,(-50,0))
		if self.img != None:
			self.factory.surf.blit(self.img, positionp+self.entity.s)
		pygame.draw.rect(self.factory.surf,black,position + self.entity.w,1)
class SpriteFactory:
	def __init__(self,surf,origin):
		"a sprite factory has the main surface surf, and origin point in camera"
		self.surf = surf
		self.sprites = []
		self.origin = origin
	def make(self,entity,img=None):
		"makes sprite components for entity"
		s = Sprite(self,entity,img)
		self.sprites.append(s)
		entity.sprite = s
		return s
	def draw(self):
		"draws all sprites"
		for s in self.sprites:
			s.draw()
# Entity is mvc
class Entity:
	def __init__(self,s=None,w=None):
		"entity has s (displacement) and w (width and height)"
		self.s = [0.0,0.0] if s == None else s
		self.w = [0.0,0.0] if w == None else w
		self.physics = None
		self.sprite = None

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
	ball = pygame.image.load('ball.gif')
	sf = SpriteFactory(surf,[320,240])
	#initial entity dumps
	entstr = ''
	while True:
		temp = socket.recv(BUFFER_SIZE)
		entstr += temp
		if len(temp) < BUFFER_SIZE:
			break
	entli = cPickle.loads(entstr)
	p1 = Entity(w=entli[0], s=entli[1])
	p2 = Entity(w=entli[2], s=entli[3])
	fl = Entity(w=entli[4], s=entli[5])
	w1 = Entity(w=entli[6], s=entli[7])
	w2 = Entity(w=entli[8], s=entli[9])
	sf.make(p1,ball)
	sf.make(p2,ball)
	sf.make(fl)
	sf.make(w1)
	sf.make(w2)
	
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
			entityli = cPickle.loads(stri)
		finally:
			pass
		p1.w = entityli[0]
		p1.s = entityli[1]
		p2.w = entityli[2]
		p2.s = entityli[3]
		fl.w = entityli[4]
		fl.s = entityli[5]
		w1.w = entityli[6]
		w1.s = entityli[7]
		w2.w = entityli[8]
		w2.s = entityli[9]
		
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
