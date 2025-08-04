import pygame

from settings import *

class DungeonCameraGroup(pygame.sprite.Group):
	'''
	aligns view with player - player character always in centre of screen
	'''
	def __init__(self):
		super().__init__()
		self.display_surf = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()

	def custom_draw(self, player):
		# centers player in middle of the screen at all times

		# calculates distance between player center and display surface center
		self.offset.x = player.rect.centerx - (SCREEN_WIDTH // 2)
		self.offset.y = player.rect.centery - (SCREEN_HEIGHT // 2)

		for sprite in sorted(self.sprites(), 
			key=lambda sprite: (sprite.depth, sprite.rect.centery)):
			# sorts sprites by their depth (layer), then by their y position
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surf.blit(sprite.image, offset_pos)
			# everything but player is moved when player moves, offset used to move everything else

	def enemy_update(self, player):
		# calls update method for all enemies in relation to player
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(
			sprite, 'type') and sprite.type == 'enemy'] # creates list of enemy sprites
		for enemy in enemy_sprites:
			enemy.enemy_update(player)
			if enemy.aoe_attack:
				# if enemy sprite currently has an attack sprite of its own
				if enemy.state == 'attack_prepare':
					# and is preparing the attack, then continue updating the attack
					enemy.aoe_attack.update_alpha()
				else:
					# and is not attacking, then remove the attack sprite
					enemy.aoe_attack.kill()


class ForestCameraGroup(pygame.sprite.Group):
	'''
	player remains in view, but camera is fixed
	'''
	def __init__(self):
		super().__init__()
		self.display_surf = pygame.display.get_surface()

		# uses a set background image, unlike the dungeon which uses only tiles
		self.floor_surf = pygame.image.load('graphics/level/forestmap.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft=(0,0))	

	def custom_draw(self, player):
		# screen does not move when player moves
		self.display_surf.blit(self.floor_surf,self.floor_rect)
		player.hitbox.clamp_ip(self.floor_rect)	# player cannot go out of bounds
		for sprite in sorted(self.sprites(), 
			key=lambda sprite: (sprite.depth, sprite.rect.centery)):
			self.display_surf.blit(sprite.image, sprite.rect)