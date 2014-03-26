from operator import sub,mul,add,div
import copy
import pygame
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
		self.onDuck = False
	def update(self):
		"update the physics component of entity"
		self.v[1] += self.gravity
		originals = self.entity.s
		self.entity.s = map(add,self.entity.s, [v/30.0 for v in self.v])
		self.v[0] *= 0.70
		self.onFloor = False
		if -1. < self.v[0] and self.v[0] < 1.:
			self.stop()
	def push(self, speed):
		"function that makes the player walk or run (also changes sprite animation)"
		self.v[0] += speed
		#print self.entity.a
		if speed > 0.0 and self.entity.a['state'] != 1:
			self.entity.a = {'state':1, 'time':0}
		elif speed < 0.0 and self.entity.a['state'] != 2:
			self.entity.a = {'state':2, 'time':20}
		self.controlled = True
	def stop(self):
		"function that indicates the sprite animation to stop"
		if self.entity.a['state'] == 1 or self.entity.a['state'] == 2:
			if self.onDuck:
				self.entity.a = {'state':3, 'time':1}
			else:
				self.entity.a = {'state':0, 'time':0}
	def jump(self, speed):
		"function that makes the player jump"
		if self.onFloor:
			self.v[1] += speed
			self.entity.s[1] -= 1
			self.controlled = True
	def duck(self):
		"function for player ducking"
		self.entity.w[1] = 60
		self.entity.s[1] += 20
		self.onDuck = True
		if self.entity.a['state'] != 3:
			self.entity.a = {'state':3, 'time':1}
	def unduck(self):
		"function for player unducking after a ducking"
		self.entity.w[1] = 100
		self.entity.s[1] -= 20
		self.onDuck = False
		if self.entity.a['state'] != 0:
			self.entity.a = {'state':0, 'time':0}
	def attack(self,target):
		"dummy function"
		if self.entity.a['state'] != 4:
			self.entity.a = {'state':4, 'time':0}
		#print target.health
	def resolve(self, jp):
		"function that resolves player's collision with another player `jp'"
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
	def __init__(self,factory,entity,imageset=None):
		"a sprite has parent factory and parent entity"
		self.imageset = imageset
		self.factory = factory
		self.entity = entity
	def getImage(self):
		"gets appropriate image from the set of images (animation and all)"
		a = self.entity.a
		newImage = None
		if a['time'] == 0:
			a['state'] = 0
			newImage = self.imageset[0][0]
		elif a['state'] == 1:
			newImage = self.imageset[1][a['time']]
			newImage.set_colorkey(white)
		elif a['state'] == 2:
			newImage = self.imageset[1][a['time']]
			newImage.set_colorkey(white)
		elif a['state'] == 3:
			newImage = self.imageset[2][0]
			newImage.set_colorkey(white)
		elif a['state'] == 4:
			newImage = self.imageset[3][a['time']]
		else:
			newImage = self.imageset[0][0]
		newImage.set_colorkey(white)
		newImage = newImage.convert()
		if self.entity.id == 1:
			player2pos = self.factory.sprites[1].entity.s[0]
			if self.entity.s[0] - player2pos >= 0:
				return pygame.transform.flip(newImage, True, False)
		else:
			player1pos = self.factory.sprites[0].entity.s[0]
			if self.entity.s[0] - player1pos >= 0:
				return pygame.transform.flip(newImage, True, False)
		
		return newImage
	def draw(self):
		"draws the sprite component of entity"
		corner1,corner2 = getCorners(self.entity)
		position = map(add,corner1,self.factory.origin)
		positionp = map(add,position,(-50,0))
		if self.imageset != None:
			self.factory.surf.blit(self.getImage(), positionp+self.entity.s)
		pygame.draw.rect(self.factory.surf,black,position + self.entity.w,1)
class SpriteFactory:
	def __init__(self,surf,origin,specials):
		"a sprite factory has the main surface surf, and origin point in camera"
		self.surf = surf
		self.sprites = []
		self.origin = origin
		self.bg = specials[0]
	def make(self,entity,img=None):
		"makes sprite components for entity"
		s = Sprite(self,entity,img)
		self.sprites.append(s)
		entity.sprite = s
		return s
	def draw(self):
		"draws all sprites"
		hp = [100,100]
		redhp = [100,100]
		self.surf.blit(self.bg, (0,0,100,100))
		for s in self.sprites:
			s.draw()
			if s.entity.health != None:
				hp[s.entity.id-1] = s.entity.health
		# magic sprite drawing shit [#MAGIC IN PROGRESS#]pygame.draw.rect(self.surf,black,(0,0,100,100),1)
		pygame.draw.rect(self.surf,black,(0,0,100,20),0)
		pygame.draw.rect(self.surf,red,(0,0,redhp[0],20),0)
		pygame.draw.rect(self.surf,blue,(0,0,hp[0],20),0)
		pygame.draw.rect(self.surf,black,(0,30,100,20),0)
		pygame.draw.rect(self.surf,red,(0,30,redhp[1],20),0)
		pygame.draw.rect(self.surf,green,(0,30,hp[1],20),0)
class Entity:
	def __init__(self,id=None,s=None,w=None,a=None,health=None):
		"entity has s (displacement) and w (width and height) and a (animation state)"
		self.id = None if id == None else id
		self.s = [0.0,0.0] if s == None else s
		self.w = [0.0,0.0] if w == None else w
		self.a = {'state':0,'time':0} if a == None else a
		self.health = None if health == None else health
		self.physics = None
		self.sprite = None
	def updateAnimation(self):
		"decreases the animation timer by 1 as an update"
		if self.a['state'] == 1:
			self.a['time'] += 1
			if self.a['time'] >= 21:
				self.resetAnimation()
		elif self.a['state'] == 2:
			self.a['time'] -= 1
			if self.a['time'] < 0:
				self.resetAnimation()
		elif self.a['state'] == 4:
			self.a['time'] += 1
			if self.a['time'] >= 12:
				self.resetAnimation()
		else:
			pass
	def resetAnimation(self):
		if self.physics.onDuck:
			self.a['state'] = 3
			self.a['time'] = 1
		else:
			self.a['state'] = 0
			self.a['time'] = 0
