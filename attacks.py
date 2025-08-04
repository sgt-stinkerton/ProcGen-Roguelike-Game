import pygame

from settings import *

class Sword(pygame.sprite.Sprite):
	'''
	sword attack hitbox
	'''
	def __init__(self, player, groups):
		super().__init__(groups)
		self.type = 'sword'
		self.direction = player.state.split('_')[0]
		path = 'graphics/attacks/sword/' + self.direction + '_hitbox.png'
		# hitbox uses images to make it a sprite, so that sprite collision
		# checks can be made (and sprite groups iterated over)
		self.image = pygame.image.load(path).convert_alpha()
		self.rect = self.image.get_rect(center=player.rect.center)
		self.update_atk(player)

	def update_atk(self, player):
		# aligns atk hitbox with current player direction and position
		if self.direction == 'up':
			self.rect.midbottom = player.rect.center + pygame.math.Vector2(0,10)
		elif self.direction == 'down':
			self.rect.midtop = player.rect.center + pygame.math.Vector2(0,4)
		elif self.direction == 'left': 
			self.rect.midright = player.rect.center + pygame.math.Vector2(5,7)
		else:
			self.rect.midleft = player.rect.center + pygame.math.Vector2(-5,7)


class Magic(pygame.sprite.Sprite):
	'''
	magic attack sprite
	'''
	def __init__(self, player, groups):
		super().__init__(groups)
		self.type = 'magic'
		self.depth = LAYERS['mid_layer']

		# magic sprite has its own animation, requires frame changing
		self.frame_index = 0
		self.animation_speed = 0.2
		self.animation = import_folder('graphics/attacks/magic')
		self.image = self.animation[self.frame_index]
		self.rect = self.image.get_rect(center=player.hitbox.midbottom)

	def update_atk(self, player, double=False):
		# updates magic animation
		self.frame_index = (self.frame_index + self.animation_speed) % len(self.animation)
		self.image = self.animation[int(self.frame_index)]
		if double:
			# for example player - player image scaled, so magic needs to also be scaled
			self.image = pygame.transform.scale_by(self.image, 2)
		self.rect = self.image.get_rect(center=player.hitbox.midbottom)

class AOE(pygame.sprite.Sprite):
	'''
	sprite which fades in as enemy aoe attack is prepared
	'''
	def __init__(self, pos, groups):
		super().__init__(groups)

		# attack image setup
		self.image = pygame.image.load('graphics/attacks/enemy/aoe.png').convert_alpha()
		self.rect = self.image.get_rect(center=pos)
		self.depth = LAYERS['mid_layer']
		self.type = 'aoe'

		# fade setup
		self.alpha = 0
		self.image.set_alpha(self.alpha)

	def update_alpha(self):
		# fades in the attack circle
		self.alpha += AOE_FADE_VAL
		self.image.set_alpha(self.alpha)