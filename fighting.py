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
# Physics is model
class Physics:
	def __init__(self,entity,kind,v,gravity):
		"a physics component has a parent entity, a kind (floor,wall or player),v (velocity), and gravity"
		self.entity = entity
		self.kind = "floor" if kind == None else kind
		self.v = [0.0,0.0] if v == None else v
		self.gravity = 0.0 if gravity == None else gravity
	def update(self):
		"update the physics component of entity"
		self.v[1] += self.gravity
		self.entity.s = map(add,self.entity.s, [v/30.0 for v in self.v])
class PhysicsFactory:
	def __init__(self):
		"a physics factory only has the physicses"
		self.physicses = [] 
	def make(self,entity,v=None,gravity=None,kind=None):
		"makes a new physics component for an entity"
		p = Physics(entity,kind,v,gravity)
		entity.physics = p
		self.physicses.append(p)
		return p
	def update(self):
		"update all physics components"
		for p in self.physicses:
			p.update()
	def onFloor(self,entity):
		floor = False
		for j in xrange(len(self.physicses)):
			spje = self.physicses[j].entity
			if spje == entity:
				continue
			if spje.physics.kind == "floor":
				spie1,spie2 = getCorners(entity)
				spje1,spje2 = getCorners(spje)
				floor = floor or (strictlygreater(spie2,spje1) and strictlygreater(spje2,spie1))
		return floor
	def resolve(self,entity1,entity2):
		"resolves collisions of entity to all physics components"
		spi = entity1.physics
		spie = spi.entity
		spj = entity2.physics
		spje = spj.entity
		spie1,spie2 = getCorners(spie)
		spje1,spje2 = getCorners(spje)
		if strictlygreater(spie2,spje1) and strictlygreater(spje2,spie1):
			# enter here if two bounding boxes collide
			if spj.kind == "floor":
				# enter here if target bounding box is a floor
				if spje2[1] > spie2[1]:
					spie.s[1] = spje.s[1] - (spje.w[1] + spie.w[1])/2
					spi.v[1] = 0
				else:
					spie.s[1] = spje.s[1] + (spje.w[1] + spie.w[1])/2
					spi.v[1] = 0				
			else:
				# enter here if target bounding box is anything else	
				if spje2[0] > spie2[0]:
					spie.s[0] = spje.s[0] - (spje.w[0] + spie.w[0])/2					
					spi.v[0] = 0
					spj.v[0] = 0
				else:
					spie.s[0] = spje.s[0] + (spje.w[0] + spie.w[0])/2
					spi.v[0] = 0
					spj.v[0] = 0
# Sprite is view
class Sprite:
	def __init__(self,factory,entity):
		"a sprite has parent factory and parent entity"
		self.factory = factory
		self.entity = entity
	def draw(self):
		"draws the sprite component of entity"
		corner1,corner2 = getCorners(self.entity)
		position = map(add,corner1,self.factory.origin)
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
# Entity is mvc
class Entity:
	def __init__(self,s=None,w=None):
		"entity has s (displacement) and w (width and height)"
		self.s = [0.0,0.0] if s == None else s
		self.w = [0.0,0.0] if w == None else w
		self.physics = None
		self.sprite = None

def __main__():
	pygame.init()
	fpsClock = pygame.time.Clock()
	surf = pygame.display.set_mode((640,480))
	pygame.display.set_caption("Game")
	# make all the factories
	pf = PhysicsFactory()
	sf = SpriteFactory(surf,[320,240])
	# make all the entities
	player1 = Entity(w=[50.0,100.0])
	player2 = Entity(w=[50.0,100.0],s=[100.0,0.0])
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
	# game loop
	while True:
		surf.fill(white)
		sf.draw()
		pygame.display.update()
		pf.update()
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			# controller for players
			movingplayer = 0
			if event.type == KEYDOWN:
				if event.key == K_LEFT:
					player1.physics.v[0] = -100.0	
					movingplayer = 1
				if event.key == K_RIGHT:
					player1.physics.v[0] = 100.0
					movingplayer = 1
				if event.key == K_a:
					player2.physics.v[0] = -100.0
					movingplayer = 2 if movingplayer != 1 else 0
				if event.key == K_d:
					player2.physics.v[0] = 100.0
					movingplayer = 2 if movingplayer != 1 else 0
				if event.key == K_UP:
					if pf.onFloor(player1):
						player1.physics.v[1] = -300.0
						player1.s[1] -= 1
				if event.key == K_w:
					if pf.onFloor(player2):
						player2.physics.v[1] = -300.0
						player2.s[1] -= 1
			if event.type == KEYUP:
				if event.key == K_LEFT:
					player1.physics.v[0] = 0.0
				if event.key == K_RIGHT:
					player1.physics.v[0] = 0.0
				if event.key == K_a:
					player2.physics.v[0] = 0.0
				if event.key == K_d:
					player2.physics.v[0] = 0.0
		if movingplayer == 0:
			if not pf.onFloor(player1) and pf.onFloor(player2):
				movingplayer = 1			
			elif pf.onFloor(player1) and not pf.onFloor(player2):
				movingplayer = 2
		if movingplayer == 1:
			pf.resolve(player1, player2)
		elif movingplayer == 2:
			pf.resolve(player2, player1)
		else:
			pf.resolve(player1, player2)
		for e in [floor,wall1,wall2]:
			pf.resolve(player1, e)
			pf.resolve(player2, e)
		fpsClock.tick(60)

__main__()
