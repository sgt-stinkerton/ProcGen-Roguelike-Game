import pygame

from settings import *

class Overlay:
	'''
	creates 3 bars always visible on player's screen (in forest and dungeon):
	health, mana, and stamina
	'''
	def __init__(self, player):
		self.display_surface = pygame.display.get_surface()

		# each bar has specific position on player's screen
		self.hp_bar = pygame.Rect(
			(20,20), (player.stats['health']*5, 16))
		self.mana_bar = pygame.Rect(
			(20,46), (player.stats['mana_amt']*5, 16))
		self.stamina_bar = pygame.Rect(
			(0,0), (player.stats['stamina']*8, 16))
		self.stamina_bar.center = (MID_W,650)

	def display_bar(self, current, max, bg, colour):
		pygame.draw.rect(self.display_surface, BLACK, bg)

		# calculates how much of bar should be coloured (dependent on player stats)
		ratio = current / max
		current_width = (bg.width - 8) * ratio
		current = bg.copy()
		current.width = current_width
		current.height = current.height - 8
		
		# stamina bar reduces from either side, not just one, so reduction in size taken from
		# both ends of the bar
		if colour == STAMINA_COL:
			current.center = (MID_W, current.centery+4)
		else:
			current.topleft = (current.x + 4, current.y + 4)

		pygame.draw.rect(self.display_surface, colour, current)

	def display(self, player):
		# displays each bar
		self.display_bar(player.health, 
			player.stats['health'], self.hp_bar, HP_COL)
		self.display_bar(player.stamina, 
			player.stats['stamina'], self.stamina_bar, STAMINA_COL)
		self.display_bar(player.mana, 
			player.stats['mana_amt'], self.mana_bar, MANA_COL)


class TextBubble:
	'''
	defines a text bubble which appears above the player's head either
	- when they are near something that can be interacted with
	- or when they are unable to dash due to low stamina
	'''
	def __init__(self, text, pos=None):
		self.display_surface = pygame.display.get_surface()
		self.depth = LAYERS['foreground']
		self.create_text(text)
		self.create_bubble()
		self.pos_bubble(pos)

	def create_text(self, text):
		# creates text displayed on the bubble
		self.font = pygame.font.Font(UI_FONT, TEXT_XS)
		self.text_surf = self.font.render(text, False, BLACK)
		self.text_rect = self.text_surf.get_rect()

	def create_bubble(self):
		# creates the bubble
		self.bubble_rect = self.text_rect.copy()
		self.bubble_rect.height += 5
		self.bubble_rect.width += 10

	def pos_bubble(self, pos):
		# positions bubble above player head
		if not pos:
			self.bubble_rect.topleft = (530,320)
		else:
			self.bubble_rect.topleft = pos
		self.text_rect.center = self.bubble_rect.center

	def custom_draw(self, player=None):
		# positions bubble above player head if in forest, and draws bubble
		if player:
			self.bubble_rect.bottomleft = player.rect.topleft + pygame.math.Vector2(25,-2)
			self.text_rect.center = self.bubble_rect.center

		pygame.draw.rect(self.display_surface, WHITE, 
			self.bubble_rect, border_radius=10)		# bubble rect given rounded edges
		self.display_surface.blit(self.text_surf, self.text_rect)