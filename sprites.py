import pygame
from copy import deepcopy

from settings import *
from player_store import TempStore
from attacks import AOE
from math import cos


class Tile(pygame.sprite.Sprite):
	'''
	basic tile  class - used for all tile sprites
	'''
	def __init__(self, pos, surface, groups, depth=LAYERS['main'], type=None):
		super().__init__(groups)
		self.image = surface
		self.rect = self.image.get_rect(topleft=pos)
		self.depth = depth							# visual layer depth
		self.hitbox = self.rect.inflate(0, -10)		# so that player sprite appears in front of tiles
		self.type = type 							# some tiles have specific use, referred to using specific type


class TileSheet:
	'''
	loads tile from tilesheet
	'''
	def __init__(self,filename):
		# loads entire sheet (called only once, so that image doesnt have to be loaded multiple times)
		self.sheet = pygame.image.load(filename).convert_alpha()

	def get_image(self,pos_on_sheet):
		# extracts tile from tilesheet (as subsurface), returns as image
		image = self.sheet.subsurface(pygame.Rect(
			(pos_on_sheet[0]-1)*TILE_SIZE,			# pos_on_sheet starts from 1 (easier to read) so decremented by 1,
			(pos_on_sheet[1]-1)*TILE_SIZE, 			# then * tile size to reflect position of top left pixel on sheet
			TILE_SIZE,TILE_SIZE))
		return image


class Entity(pygame.sprite.Sprite):
	'''
	parent class for all moving sprites
	'''
	def __init__(self,groups):
		super().__init__(groups)
		self.frame_index = 0 					# animations begin on frame 0
		self.animation_speed = 0.2
		self.direction = pygame.math.Vector2()  # used for movement direction

	def move(self, speed):
		if self.direction.magnitude() != 0:
			# makes diagonal speed same as when entity is moving horizontally/vertically
			self.direction = self.direction.normalize()

		# moves sprite (using hitbox) by multiplying the movement speed and the direction
		self.hitbox.x += self.direction.x * speed
		self.collision('x')
		self.hitbox.y += self.direction.y * speed
		self.collision('y')

		# aligns sprite image with hitbox, as image not being moved - hitbox is
		self.rect.center = self.hitbox.center

	def collision(self, direction):
		# checking the hitbox of the sprite against hitbox of entity
		# so that entity cannot walk through walls

		for sprite in self.collision_sprites:
			if sprite.hitbox.colliderect(self.hitbox):
				# loops through every sprite hitbox, checks if colliding with entity
				if direction == 'x':
					if self.direction.x > 0:  					# moving right
						self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0:  					# moving left
						self.hitbox.left = sprite.hitbox.right
				elif direction == 'y':
					if self.direction.y > 0:  					# moving down
						self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0:  					# moving up
						self.hitbox.top = sprite.hitbox.bottom

	def import_assets(self, path):
		# imports list of surfaces (images) for each animation, stored in
		# animation dictionary
		for animation in self.animations.keys():
			full_path = path + animation
			self.animations[animation] = import_folder(full_path)

	def get_state(self):
		# changes state according to current move - used by Player and ExamplePlayer
		# enemy uses different get_state method

		if self.direction.x == 0 and self.direction.y == 0:
			# not moving
			if not any(state in self.state for state in self.action_states):
				# not performing any action, reset state to idle
				self.state = self.state + '_idle'
				return

		# checks other possible actions that could be performed
		action_map = {
		'_sword': self.sword, '_dash': self.dashing, '_magic': self.magic}
		for state, action in action_map.items():
			self.change_state(state, action)

	def change_state(self, state, is_current):
		# changes state in accordance with get_state - used by Player and ExamplePlayer

		if is_current:
			# if the action is being performed
			if not state in self.state:
				# if the state mapped to the action is not the player's current state
				for s in self.action_states:
					# check through possible states
					if s in self.state:
						# if current searched state is one that is in the possible states
						# replace current state with state that player should be in
						self.state = self.state.replace(s,state)
						break
				else:
					self.state += state
		else:
			# no action being performed
			if state in self.state:
				# but player still in state of action (sword,dash,magic)
				self.state = self.state.replace(state,'')

	def animate(self):
		# animates the sprite's current state - used by Player and Enemy
		# ExamplePlayer uses slightly altered version

		animation = self.animations[self.state]
		self.frame_index = (self.frame_index + self.animation_speed) % len(animation)
		# % len(animation) ensures that index does not exceed number of animation frames
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center=self.hitbox.center)


class Player(Entity):
	'''
	the player character which is controllable by the user
	'''
	def __init__(self, pos, groups, collision_sprites, create_atk, destroy_atk, data_store, stamina_warning):
		super().__init__(groups)

		# importing player data
		self.data_store = data_store

		# animation - each animation has different version for different direction
		self.animations = {'up': [],'down': [],'left': [],'right': [], 			# movement
		'right_idle': [],'left_idle': [],'up_idle': [],'down_idle': [],			# idle
		'up_sword': [],'down_sword': [],'left_sword': [],'right_sword': [],		# sword attack
		'up_magic': [], 'down_magic': [], 'left_magic': [], 'right_magic': [],	# magic attack
		'up_dash': [],'down_dash': [],'left_dash': [],'right_dash': []}			# dash	

		# graphics
		self.import_assets('graphics/player/')
		self.state = 'down'
		self.action_states = ['_idle','_sword','_magic','_dash']
		self.image = self.animations[self.state][self.frame_index]

		# collisions and visuals
		self.rect = self.image.get_rect(topleft=pos)
		self.hitbox = self.rect.inflate(-2, -14)	# smaller hitbox for player sprite to overlap with tiles
		self.collision_sprites = collision_sprites	# 
		self.depth = LAYERS['main']
		self.pos = pygame.math.Vector2(self.rect.center)

		# state functions
		self.create_atk = create_atk			# called when player performs attack
		self.destroy_atk = destroy_atk 			# called when player attack is finished
		self.stamina_warning = stamina_warning 	# called when player is too low on stamina to dash

		# sword
		self.sword = False
		self.atk_time = 0 			# time since last sword attack
		self.atk_duration = 360

		# magic
		self.magic = False
		self.magic_time = 0 		# time since last magic attack
		self.magic_duration = 420

		# dash
		self.dashing = False
		self.dash_time = 0 			# time since last dash
		self.dash_distance = 80
		self.dash_duration = 200

		# vulnerability
		self.vulnerable = True
		self.hit_time = 0 			# time since last taken damage
		self.invul_duration = 400

		# maximum values that stats can reach
		self.max_stats = {
		'health': 50,
		'attack': 30,
		'mana': 0.2,  
		'stamina': 80}

		# stat upgrade amount and cost
		# [amount increased by, cost of upgrade]
		self.upgrade = {
		'health': [10,20],
		'attack': [5,10],
		'mana': [0.05,25],  
		'stamina': [5,5]}
		
		# stats imported from data_store
		self.stats = {}
		self.import_stats()
		self.health = self.stats['health']
		self.mana = self.stats['mana_amt']
		self.stamina = self.stats['stamina']
		self.speed = self.stats['speed']

	def import_stats(self):
		# get data from storage
		self.stats = deepcopy(self.data_store.get_current())

	def export_stats(self):
		# place data in storage
		self.data_store.update_current(self.stats)

	def input(self):
		# get player input
		keys = pygame.key.get_pressed()
		mouse = pygame.mouse.get_pressed()

		if not self.sword and not self.magic:
			# so player cannot change direction when attacking

			# vertical movement
			if keys[pygame.K_w]:
				self.direction.y = -1
				self.state = 'up'
			elif keys[pygame.K_s]:
				self.direction.y = 1
				self.state = 'down'
			else:
				self.direction.y = 0

			# horizontal movement
			if keys[pygame.K_a]:
				self.direction.x = -1
				self.state = 'left'
			elif keys[pygame.K_d]:
				self.direction.x = 1
				self.state = 'right'
			else:
				self.direction.x = 0

			# sword attack
			if mouse[0]:
				self.sword = True
				self.atk_time = pygame.time.get_ticks()
				self.create_atk('sword')
				self.frame_index = 0

			# magic attack
			if mouse[2]:
				if self.mana >= MAGIC_MANA:
					self.magic = True
					self.magic_time = pygame.time.get_ticks()
					self.create_atk('magic')
					self.frame_index = 0
					self.mana -= MAGIC_MANA

			# dash
			if keys[pygame.K_SPACE] and not self.dashing:
				if self.stamina >= DASH_STAMINA:
					if self.dash_collision_rect():
						self.dashing = True
						self.dash_time = pygame.time.get_ticks()
						self.vulnerable = False
						self.frame_index = 0
						self.stamina -= DASH_STAMINA
				else:
					self.stamina_warning('on_press')

		else:
			# player still able to move during attacks, just cannot change 
			# direction (makes aligning attack hitboxes simpler)

			# vertical movement
			if keys[pygame.K_w]:
				self.direction.y = -1
			elif keys[pygame.K_s]:
				self.direction.y = 1
			else:
				self.direction.y = 0
			# horizontal movement
			if keys[pygame.K_a]:
				self.direction.x = -1
			elif keys[pygame.K_d]:
				self.direction.x = 1
			else:
				self.direction.x = 0
			
	def dash_collision_rect(self):
		# checking collision specifically for dash

		if self.direction.x == 0 and self.direction.y == 0:
			# can't dash, as player not moving in any direction
			return False

		# creates one/two rects which cover the length of the player's dash
		# used to check if there are no obstructions in the dash path
		y_check = pygame.Rect((-100,-100),(
			self.hitbox.width,self.dash_distance))
		x_check = pygame.Rect((-100,-100),(
			self.dash_distance,self.hitbox.height))

		# aligning the collision checker(s) with player hitbox
		if self.direction.x > 0:
			x_check.topleft = self.hitbox.topright
		elif self.direction.x < 0:
			x_check.topright = self.hitbox.topleft
		if self.direction.y > 0:
			y_check.topleft = self.hitbox.bottomleft
		elif self.direction.y < 0:
			y_check.bottomleft = self.hitbox.topleft

		# joining separate rects / renaming single direction checks for simplicity
		if self.direction.x != 0 and self.direction.y != 0:
			full_check = x_check.union(y_check)
			# union of rects fills diagonal space dash space
		else:
			if self.direction.x != 0:
				full_check = x_check.copy()
			elif self.direction.y != 0:
				full_check = y_check.copy()

		# checking for collisions between check rect and collision sprites
		can_dash = True
		for sprite in self.collision_sprites:
			if sprite.hitbox.colliderect(full_check):
				can_dash = False

		# aligning player hitbox to collision checker
		if can_dash:
			if self.direction.x > 0:
				self.hitbox.right = full_check.right
			elif self.direction.x < 0:
				self.hitbox.left = full_check.left
			if self.direction.y > 0:
				self.hitbox.bottom = full_check.bottom
			elif self.direction.y < 0:
				self.hitbox.top = full_check.top

		return can_dash

	def change_speed(self):
		# player movement speed changed when performing an attack
		if self.sword or self.magic:
			self.speed = 1
		else:
			self.speed = 4

	def get_atk_dmg(self, atk_type):
		# returns value of the amount of damage that the player's attack hit for
		dmg = self.stats['attack']
		if atk_type == 'magic':
			dmg += MAGIC_DMG
		return dmg

	def cooldowns(self):
		# checks if an action should still be being performed by 
		# calculating the time since the move was first performed and
		# comparing that to its defined duration

		current_time = pygame.time.get_ticks()

		if self.sword:
			if current_time - self.atk_time >= self.atk_duration:
				self.destroy_atk()
				self.sword = False

		elif self.dashing:
			if current_time - self.dash_time >= self.dash_duration:
				self.dashing = False
				self.vulnerable = True

		elif self.magic:
			if current_time - self.magic_time >= self.magic_duration:
				self.destroy_atk()
				self.magic = False

		if not self.vulnerable:
			if current_time - self.hit_time >= self.invul_duration:
				self.vulnerable = True

	def recovery(self):
		# gradual recovery of player stats
		if self.stamina + 0.15 > self.stats['stamina']:
			self.stamina = self.stats['stamina']
		else:
			self.stamina += 0.15
			
		if self.mana + self.stats['mana'] > self.stats['mana_amt']:
			self.mana = self.stats['mana_amt']
		else:
			self.mana += self.stats['mana']

	def on_hit(self):
		# player flickers when invulnerable except for when dashing
		if not self.vulnerable and not self.dashing:
			value = cos(pygame.time.get_ticks())
			# if value from cos graph at current point of time is positive
			if value >= 0:
				self.image.set_alpha(255)
			else:
				self.image.set_alpha(0)
		else:
			self.image.set_alpha(255)

	def update(self):
		self.input()
		self.on_hit()
		self.stamina_warning('check')
		self.cooldowns()
		self.get_state()
		self.change_speed()
		self.animate()
		self.move(self.speed)
		self.recovery()


class ExamplePlayer(Entity):
	'''
	used in tutorial to show player various moves that can be performed
	comments made where differences between regular player and exampleplayer are
	'''
	def __init__(self, pos, groups, example_type, magic_atk, destroy_atk):
		super().__init__(groups)

		# animations - less animations need to be imported as examples only face one direction
		self.animations = {'down': [], 'down_idle': [], 
		'down_sword': [], 'down_magic': [], 'down_dash': []}

		# graphics
		self.import_assets('graphics/player/')
		self.example_type = example_type
		self.state = 'down_idle'
		self.action_states = ['_idle','_sword','_magic','_dash']
		self.image = self.animations[self.state][self.frame_index]
		self.image = pygame.transform.scale_by(self.image, 2)	# scaled the image for better visibility	

		# collisions and visuals
		self.rect = self.image.get_rect(topleft=pos)
		self.hitbox = self.rect.inflate(-2, -14)
		self.depth = LAYERS['main']
		self.pos = pygame.math.Vector2(self.rect.center)
		self.last_action = 0
		self.between_actions = 1000

		# sword
		self.sword = False 
		self.atk_time = 0
		self.atk_duration = 360

		# magic
		self.magic_atk = magic_atk
		self.destroy_atk = destroy_atk
		self.magic = False
		self.magic_time = 0
		self.magic_duration = 420

		# dash
		self.dashing = False
		self.dash_time = 0
		self.dash_duration = 200

		# movement
		self.speed = 4

	def example(self):
		# replaces input method from player class

		if self.example_type == 'move':
			self.direction.y = 1
			self.state = 'down'

		if self.action_cooldown():
			if not self.sword and not self.magic and not self.dashing:
				self.last_action = pygame.time.get_ticks()

				if self.example_type == 'sword':
					self.sword = True
					self.atk_time = pygame.time.get_ticks()

				elif self.example_type == 'magic':
					self.magic = True
					self.magic_time = pygame.time.get_ticks()
					self.magic_atk()

				elif self.example_type == 'dash':
					self.direction.y = 1
					self.dashing = True
					self.dash_time = pygame.time.get_ticks()

	def animate(self):
		animation = self.animations[self.state]
		self.frame_index = (self.frame_index + self.animation_speed) % len(animation)
		self.image = animation[int(self.frame_index)]
		self.image = pygame.transform.scale_by(self.image, 2)		# scales image so example more visible
		self.rect = self.image.get_rect(center=self.hitbox.center)

	def action_cooldown(self):
		# examples repeat moves indefinitely, only need to know how long to
		# wait until next attack can be performed
		current_time = pygame.time.get_ticks()
		if current_time - self.last_action < self.between_actions:
			return False
		return True

	def cooldowns(self):
		current_time = pygame.time.get_ticks()

		if self.sword:
			if current_time - self.atk_time >= self.atk_duration:
				self.sword = False

		if self.dashing:
			if current_time - self.dash_time >= self.dash_duration:
				self.dashing = False

		if self.magic:
			if current_time - self.magic_time >= self.magic_duration:
				self.destroy_atk()
				self.magic = False

	def update(self):
		# doesn't take player input or check for collisions, 
		# as player cannot control the example characters
		self.example()
		self.cooldowns()
		self.get_state()
		self.animate()


class Enemy(Entity):
	'''
	enemies which player can attack / get hit by in dungeon
	'''
	def __init__(self, pos, groups, collision_sprites, all_sprites, dmg_player, heal_player, add_wisps):
		super().__init__(groups)
		
		# animations
		self.animations = {'idle': [], 'move': [],'attack': [], 
		'attack_prepare': [], 'attack_idle': [], 'return': []}

		# graphics
		self.import_assets('graphics/enemy/')
		self.state = 'idle'
		self.image = self.animations[self.state][self.frame_index]
		self.depth = LAYERS['main']

		# movement and collisions
		self.rect = self.image.get_rect(topleft=pos)
		self.hitbox = self.rect.copy()
		self.collision_sprites = collision_sprites
		self.all_sprites = all_sprites
		self.obstacles = None 						# list of tiles which obstruct enemy vision

		# enemy data
		self.type = 'enemy'
		self.health = ENEMY['health']
		self.attack = ENEMY['attack']
		self.speed = ENEMY['speed'] 
		self.atk_radius = ENEMY['attack radius'] 	# distance from player which enemy will attempt to attack at
		self.ctn_radius = ENEMY['caution radius'] 	# disance from player which enemy will follow player at
		self.return_pos = pos 	# position which enemy will return to when player is out of range

		# state functions
		self.dmg_player = dmg_player
		self.heal_player = heal_player
		self.add_wisps = add_wisps
		self.aoe_attack = None

		# attacking
		self.atk_time = 0			# time since last attack
		self.atk_cooldown = 800		# time to cool down after attack
		self.prepared = False		# attack has been prepared
		self.prep_time = 0 			# time since started preparing
		self.full_prep = 700		# amount of time it takes to fully prep attack

		# vulnerability
		self.vulnerable = True 		# can take damage
		self.invul_time = 0 		# time since last hit
		self.invul_duration = 560 	# duration of invulnerability

	def get_dist_dir(self, pos):
		# returns the distance and direction of a point pos from enemy's position
		enemy_vec = pygame.math.Vector2(self.rect.center)
		end_vec = pygame.math.Vector2(pos)
		distance = enemy_vec.distance_to(end_vec)

		if distance:
			# gets direction towards point from enemy's current point
			direction = (end_vec - enemy_vec).normalize()
		else:
			# clear direction, not moving in any direction
			direction = pygame.math.Vector2()

		return distance, direction

	def get_state(self, player):
		# changes state in accordance with own state and distance to player

		dist_to_player = self.get_dist_dir(player.rect.center)[0]
		if self.state != 'return' and self.can_atk():
			# if enemy not returning to initial positon and is able to attack
		    if self.prepared and self.state != 'attack':
		    	# if ready to attack but not in attack state, switch, regardless
		    	# of if player in range or not
		    	self.state = 'attack'
		    elif self.state != 'attack_prepare':
		    	# cannot be broken out of attack prep state once started
		        if dist_to_player <= self.atk_radius and not self.prepared:
		        	self.state = 'attack_prepare'
		        	self.prep_time = pygame.time.get_ticks()
		        	# get time when attack started being prepped
		        	self.aoe_attack = AOE(self.rect.center, self.all_sprites)
		        elif dist_to_player <= self.ctn_radius:
		        	# player in notice range, move towards them (to get in attack range)
		        	self.state = 'move'
		        else:
		        	# if player out of range, check if at original position
		        	if not self.rect.collidepoint(self.return_pos):
		        		# return to spawn position
		        		self.state = 'return'
		        	else:
		        		# stay idle at spawn position
		        		self.state = 'idle'
		else:
			if not self.can_atk():
				# cooling down after attack, can't move
				self.state = 'attack_idle'
			else:
				if self.rect.collidepoint(self.return_pos):
					# at spawn pos, don't need to move
					self.state = 'idle'

		if self.state in ['attack','attack_idle','attack_prepare','move']:
			if self.check_obstructed(player):
				# regardless of state, enemies get 'bored' if player obstructed
				# from view or leaves room
				if not self.rect.collidepoint(self.return_pos):
					self.state = 'return'
				else:
					self.state = 'idle'

	def state_action(self,player):
		# changes certain things depending on current enemy state

		# setting direction
		if self.state == 'move':
			# move towards player
			self.direction = self.get_dist_dir(player.rect.center)[1]
		elif self.state == 'return':
			# return to start position
			self.direction = self.get_dist_dir(self.return_pos)[1]
		else:
			# unmoving in other states
			self.direction = pygame.math.Vector2()

		if self.state == 'attack':
			# check attack time and dmg player if in vicinity
			self.atk_time = pygame.time.get_ticks()
			self.prepared = False
			if self.get_dist_dir(player.rect.center)[0] <= self.atk_radius:
				self.dmg_player()

	def check_obstructed(self, player):
		# checks that no wall tiles are obstructing the enemy's view of the player
		enemy_pos = self.rect.center
		player_pos = player.rect.center

		if not self.obstacles:
			# creates list of sprites which obstruct the view of the enemy (walls and corridors)
			# using list comprehension, only done once so list not made for every check
			self.obstacles = [sprite for sprite in self.collision_sprites if hasattr(
				sprite, 'type') and (sprite.type == 'wall' or sprite.type == 'corridor')]
		
		for sprite in self.obstacles:
			if sprite.hitbox.clipline((enemy_pos,player_pos)):
				# draws line between enemy center and player center - if line touches 
				# obstacle sprite, enemy loses interest in player as it cannot see them
				return True
			# enemy can still see player
		return False

	def get_hurt(self, player, atk_type):
		# called when player attack collides with enemy hitbox
		if self.vulnerable:
			self.vulnerable = False
			self.health -= player.get_atk_dmg(atk_type)
			self.invul_time = pygame.time.get_ticks()
			
	def can_atk(self):
		# checks if enough time has passed since the last attack was performed
		current_time = pygame.time.get_ticks()
		if current_time - self.atk_time >= self.atk_cooldown:
			return True
		return False

	def cooldowns(self):
		current_time = pygame.time.get_ticks()

		# counts for how long attack should be building up for
		if self.state == 'attack_prepare' and not self.prepared:
			if current_time - self.prep_time >= self.full_prep:
				self.prepared = True

		# counts for how long enemy should be invulnerable to attacks (after hit)
		if not self.vulnerable:
			if current_time - self.invul_time >= self.invul_duration:
				self.vulnerable = True
				self.image.set_alpha(255)

	def check_death(self):
		if self.health <= 0:
			self.kill()
			self.heal_player()
			self.add_wisps()
			if self.aoe_attack:
				self.aoe_attack.kill()

	def on_hit(self):
		# entity flickers when invulnerable
		if not self.vulnerable:
			value = cos(pygame.time.get_ticks())
			# if value from cos graph at current point of time is positive
			if value >= 0:
				# set image to visible
				self.image.set_alpha(255)
			else:
				# else set image to invisible
				self.image.set_alpha(0)
		else:
			self.image.set_alpha(255)

	def update(self):
		self.on_hit()
		self.move(self.speed)
		self.animate()
		self.cooldowns()
		self.check_death()

	def enemy_update(self, player):
		# specific update method which changes enemy state using player location
		self.get_state(player)
		self.state_action(player)
