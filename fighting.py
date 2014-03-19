import pygame, sys, copy
from operator import sub,mul,add,div
from pygame.locals import *
white = pygame.Color(255,255,255)
black = pygame.Color(0,0,0)
# useful functions for physics
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
	def __init__(self,factory,entity):
		"a sprite has parent factory and parent entity"
		self.factory = factory
		self.entity = entity
	def draw(self):
		"draws the sprite component of entity"
		corner1,corner2 = getCorners(self.entity)
		position = map(add,corner1,self.factory.origin)
		positionp = map(add,position,(-50,0))
		if self.entity.img != None:
			self.factory.surf.blit(self.entity.img, positionp+self.entity.s)
		pygame.draw.rect(self.factory.surf,black,position + self.entity.w,1)
class SpriteFactory:
	def __init__(self,surf,origin):
		"a sprite factory has the main surface surf, and origin point in camera"
		self.surf = surf
		self.sprites = []
		self.origin = origin
	def make(self,entity):
		"makes sprite components for entity"
		s = Sprite(self,entity)
		self.sprites.append(s)
		entity.sprite = s
		return s
	def draw(self):
		"draws all sprites"
		for s in self.sprites:
			s.draw()
class Controller:
	def __init__(self, dictionary, downdictionary, updictionary):
		"a controller has dictionary, updictionary, downdictionary"
		self.dictionary = dictionary
		self.downdictionary = downdictionary
		self.updictionary = updictionary
		self.presses = []
		self.presstory = []
	def handle(self, events):
		"handles events of pygame"
		for event in events:
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				self.presses.append(event.key)
				try:
					self.downdictionary[event.key]()
				except KeyError:
					pass
			if event.type == KEYUP:
				self.presses.remove(event.key)
				try:
					self.updictionary[event.key]()
				except KeyError:
					pass
		for p in self.presses:
			try:
				self.dictionary[p]()
			except KeyError:
				pass
# Entity is mvc
class Entity:
	def __init__(self,img=None,s=None,w=None):
		"entity has s (displacement) and w (width and height)"
		self.s = [0.0,0.0] if s == None else s
		self.w = [0.0,0.0] if w == None else w
		self.img = None if img == None else img
		self.physics = None
		self.sprite = None

def __main__():
	pygame.init()
	fpsClock = pygame.time.Clock()
	surf = pygame.display.set_mode((640,480))
	pygame.display.set_caption("Game")
	ball = pygame.image.load('ball.gif')
	# make all the factories
	pf = PhysicsFactory()
	sf = SpriteFactory(surf,[320,240])
	# make all the entities
	player1 = Entity(ball,w=[20.0,100.0])
	player2 = Entity(ball,w=[20.0,100.0],s=[100.0,0.0])
	floor = Entity(w=[600.0,40.0], s=[0,100.0])
	wall1 = Entity(w=[140.0,600.0], s=[300.0,0.0])
	wall2 = Entity(w=[140.0,600.0], s=[-300.0,0.0])
	# make all the physics and sprites
	pf.make(player1,gravity=10.0,kind="player")
	pf.make(player2,gravity=10.0,kind="player")
	pf.make(floor,gravity=0.0,kind="floor")
	pf.make(wall1,gravity=0.0,kind="wall")
	pf.make(wall2,gravity=0.0,kind="wall")
	sf.make(player1)
	sf.make(player2)
	sf.make(floor)
	sf.make(wall1)
	sf.make(wall2)
	# make a magic-everything-controller
	controller = Controller(
		{
			K_LEFT: (lambda: player1.physics.push(-20.0)),
			K_RIGHT: (lambda: player1.physics.push(20.0)),
			K_UP: (lambda: player1.physics.jump(-300.0)),
			K_a: (lambda: player2.physics.push(-20.0)),
			K_d: (lambda: player2.physics.push(20.0)),
			K_w: (lambda: player2.physics.jump(-300.0)),
		},
		{
			K_DOWN: player1.physics.duck,
			K_s: player2.physics.duck,
		},
		{
			K_DOWN: player1.physics.unduck,
			K_s: player2.physics.unduck,
		}
		)
	# game loop
	while True:
		surf.fill(white)
		sf.draw()
		pygame.display.update()
		pf.update()
		controller.handle(pygame.event.get())
		fpsClock.tick(60)
__main__()
