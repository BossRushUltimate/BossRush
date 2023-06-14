import pygame
from settings import *
from entity import Entity
from support import import_folder

class Enemy(Entity):
# This sets up the name of the monster as well as the monster's position.
	def __init__(self,monster_name,position,groups,obstacle_sprites):

		super().__init__(groups)
		self.sprite_type = 'enemy'

# This sets up the graphics
		self.import_graphics(monster_data)
		self.status = 'idle'
		self.image = self.animations[self.status][self.frame_index]

# This gets the movement and stats of the monster.
		self.rect = self.image.get_rect(topleft = position)
		self.hitbox = self.rect.inflate(0,-10)
		self.obstacle_sprites = obstacle_sprites
		self.monster_name = monster_name
		monster_info = monster_name[self.monster_name]
		self.health = monster_info['health']
		self.experience = monster_info['exp']
		self.speed = monster_info['speed']
		self.attack_damage = monster_info['damage']
		self.resistance = monster_info['resistance']
		self.attack_radius = monster_info['attack_radius']
		self.notice_radius = monster_info['notice_radius']
		self.attack_type = monster_info['attack_type']

# This is how the player interacts with the monster
		self.can_attack = True
		self.attack_time = None
		self.attack_cooldown = 420

# This gets the graphics, I still need to update the filepath for getting the monsters to display on the screen.
	def import_graphics(self,name):
		self.animations = {'up': [], 'down':[], 'left':[], 'right':[], 'right_idle':[],
                           'left_idle':[], 'up_idle':[], 'down_idle':[], 'right_attack':[],
                           'left_attack':[], 'up_attack':[], 'down_attack':[]}
		monster_path = "NinjaAdventure/graphics/monsters/"
		for animation in self.animations.keys():
			self.animations[animation] = import_folder(monster_path + animation)

# This coordinates the direction the monster and player are facing as well as how far the player is from the monster.
	def get_player_distance_direction(self,player):
		enemy_vector = pygame.math.Vector2(self.rect.center)
		player_vector = pygame.math.Vector2(player.rect.center)
		distance = (player_vector - enemy_vector).magnitude()

		if distance > 0:
			direction = (player_vector - enemy_vector).normalize()
		else:
			direction = pygame.math.Vector2()

		return (distance,direction)

	def get_status(self, player):
		distance = self.get_player_distance_direction(player)[0]

		if distance <= self.attack_radius and self.can_attack:
			if self.status != 'attack':
				self.frame_index = 0
			self.status = 'attack'
		elif distance <= self.notice_radius:
			self.status = 'move'
		else:
			self.status = 'idle'

	def actions(self,player):
		if self.status == 'attack':
			self.attack_time = pygame.time.get_ticks()
			print('attack')
		elif self.status == 'move':
			self.direction = self.get_player_distance_direction(player)[1]
		else:
			self.direction = pygame.math.Vector2()

	def animate(self):
		animation = self.animations[self.status]
		
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			if self.status == 'attack':
				self.can_attack = False
			self.frame_index = 0

		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)

	def cooldown(self):
		if not self.can_attack:
			current_time = pygame.time.get_ticks()
			if current_time - self.attack_time >= self.attack_cooldown:
				self.can_attack = True

	def update(self):
		self.move(self.speed)
		self.animate()
		self.cooldown()

	def enemy_update(self,player):
		self.get_status(player)
		self.actions(player)