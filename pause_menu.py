import pygame

from settings import *
from buttons import Tab, GenButton, PromptButton, UpgradeButton

class PauseMenu:
	'''
	base pause menu class
	pause menu functions like game - both state machines
	'''
	def __init__(self,menu_type):
		self.type = menu_type

		self.display_surface = pygame.display.get_surface()
		self.bg = pygame.image.load(
			'graphics/ui/backgrounds/pause.png').convert_alpha()
		self.bg_rect = self.bg.get_rect(center=(MID_W,MID_H))
		self.create_self(menu_type)

	def draw_menu(self):
		self.display_surface.blit(self.bg, self.bg_rect)
		self.draw()

	def display(self, player=None):
		pass


class Stats(PauseMenu):
	'''
	stats section of pause menu
	'''
	def __init__(self,menu_type):
		super().__init__(menu_type)
		self.type = 'stats'

		self.bg = pygame.image.load(
			'graphics/ui/backgrounds/pause_stats.png').convert_alpha()

	def create_tabs(self):
		# creates tabs at the top of pause menu
		self.buttons = pygame.sprite.Group()
		self.upgrade_btns = pygame.sprite.Group()
		self.stats_tab = Tab(
			self.buttons, (150,150), 'stats', '', BLACK)
		self.general_tab = Tab(
			self.buttons, (MID_W,150), 'general', '_other', WHITE)

	def create_self(self,menu_type):
		self.text = []
		self.create_tabs()

		self.hp_rect = pygame.Rect((216,286),(71,193))
		self.hp_upgrade = UpgradeButton(
			[self.buttons, self.upgrade_btns], (192,263), 'health')

		self.stamina_rect = pygame.Rect((347,286),(71,193))
		self.stamina_upgrade = UpgradeButton(
			[self.buttons, self.upgrade_btns], (323,263), 'stamina')

		self.atk_rect = pygame.Rect((604,286),(71,193))
		self.atk_upgrade = UpgradeButton(
			[self.buttons, self.upgrade_btns], (580,263), 'attack')

		self.mana_rect = pygame.Rect((735,286),(71,193))
		self.mana_upgrade = UpgradeButton(
			[self.buttons, self.upgrade_btns], (711,263), 'mana')
		
		self.get_wisps(menu_type)

	def draw(self):
		for button in self.buttons:
			button.custom_draw()
		for text in self.text:
			text.draw(self.display_surface)

	def get_wisps(self, player):
		# displays how many wisps the player currently has to spend
		self.text.append(Text('current', 
			(MID_W,280), 
			TEXT_S, WHITE))
		self.text.append(Text('wisps:', 
			(MID_W,310), 
			TEXT_S, WHITE))
		self.text.append(Text(str(player.stats['wisps']), 
			(MID_W,365), 
			TEXT_M, WHITE))

	def display_bar(self,current,max,rect,colour):
		# creates and draws a coloured bar which displays how much of a stat
		# they have upgraded
		ratio = current / max
		current_height = rect.height * ratio
		current_rect = rect.copy()
		current_rect.height = current_height
		current_rect.midbottom = rect.midbottom
		pygame.draw.rect(self.display_surface,colour,current_rect)

	def display(self, player):
		# displays 4 bars for the 4 different stats that the player may upgrade
		self.display_bar(player.stats['health'],
			player.max_stats['health'], self.hp_rect, HP_COL)
		self.display_bar(player.stats['stamina'],
			player.max_stats['stamina'], self.stamina_rect, STAMINA_COL)
		self.display_bar(player.stats['attack'],
			player.max_stats['attack'], self.atk_rect, ATK_COL)
		self.display_bar(player.stats['mana'],
			player.max_stats['mana'], self.mana_rect, MANA_COL)

		self.get_wisps(player)


class UpgradeCheck(PauseMenu):
	'''
	verifies that the user wants to upgrade the chosen stat
	'''
	def __init__(self,menu_type):
		super().__init__(menu_type)

	def create_self(self,menu_type):
		self.type = menu_type

		self.check_bg = pygame.image.load(
			'graphics/ui/backgrounds/check_screen.png').convert_alpha()
		self.check_bg_rect = self.check_bg.get_rect(center=(MID_W,MID_H))
		self.text = (Text('upgrade ' + self.type + '?',
			(MID_W, MID_H - 40), 
			TEXT_M, CYAN))
		self.buttons = pygame.sprite.Group()
		self.yes_btn = PromptButton(
			self.buttons, (222,422), 'yes')
		self.no_btn = PromptButton(
			self.buttons, (544,422), 'no')

	def draw(self):
		self.display_surface.blit(self.check_bg, self.check_bg_rect)
		self.text.draw(self.display_surface)
		for button in self.buttons:
			button.custom_draw()


class NoUpgrade(PauseMenu):
	'''
	tells user that they cannot make the chosen upgrade, as they either
	do not have enough wisps or have already fully upgraded that stat
	'''
	def __init__(self,menu_type):
		super().__init__(menu_type)

	def create_self(self,menu_type):
		self.type = 'no_upgrade_' + menu_type

		self.check_bg = pygame.image.load(
			'graphics/ui/backgrounds/check_screen.png').convert_alpha()
		self.check_bg_rect = self.check_bg.get_rect(center=(MID_W,MID_H))
		self.text = []
		self.buttons = pygame.sprite.Group()
		self.ok_btn = PromptButton(
			self.buttons, (384,422), 'ok')

		if self.type[-4:] == 'cost':	
			text_1 = 'you do not have'
			text_2 = 'enough wisps.'
		else:
			text_1 = 'cannot upgrade stat'
			text_2 = 'any further.'

		self.text.append(Text(text_1,
			(MID_W, MID_H - 90), 
			TEXT_M, CYAN))
		self.text.append(Text(text_2,
			(MID_W, MID_H - 26), 
			TEXT_M, CYAN))

	def draw(self):
		self.display_surface.blit(self.check_bg,self.check_bg_rect)
		for text in self.text:
			text.draw(self.display_surface)
		for button in self.buttons:
			button.custom_draw()	


class General(PauseMenu):
	'''
	general section of pause menu, where player can save/leave dungeon, 
	exit to menu, and exit to desktop
	'''
	def __init__(self,menu_type):
		super().__init__(menu_type)
		self.type = 'general'

	def create_self(self,menu_type):
		self.area_type = menu_type
		self.create_tabs()

		self.main_menu = GenButton(
			self.buttons, (MID_W,395), 'main menu')
		self.exit_desktop = GenButton(
			self.buttons, (MID_W,500), 'exit to desktop')

		if self.area_type == 'forest':
			# save option visible instead of leave dungeon
			self.save_game = GenButton(
				self.buttons, (MID_W,290), 'save game')
		else:
			# leave dungeon option visible instead of save
			self.leave_dungeon = GenButton(
				self.buttons, (MID_W,290), 'leave dungeon')

	def create_tabs(self):
		self.buttons = pygame.sprite.Group()
		self.stats_tab = Tab(
			self.buttons, (150,150), 'stats', '_other', WHITE)
		self.general_tab = Tab(
			self.buttons, (MID_W,150), 'general', '', BLACK)

	def draw(self):
		for button in self.buttons:
			button.custom_draw()


class Check(PauseMenu):
	'''
	checks if user definitely wants to leave current area
	'''
	def __init__(self,menu_type):
		super().__init__(menu_type)

	def create_self(self,menu_type):
		self.exit_type = menu_type
		self.type = 'check'

		self.text = []
		self.text.append(Text('are you sure you',
			(MID_W, MID_H - 104), 
			TEXT_M, CYAN))
		self.text.append(Text('want to leave?',
			(MID_W, MID_H - 40), 
			TEXT_M, CYAN))
		self.text.append(Text('unsaved progress will be lost.',
			(MID_W, MID_H + 18), 
			TEXT_S, CYAN))

		self.check_bg = pygame.image.load(
			'graphics/ui/backgrounds/check_screen.png').convert_alpha()
		self.check_bg_rect = self.check_bg.get_rect(center=(MID_W,MID_H))
		self.buttons = pygame.sprite.Group()
		self.yes_btn = PromptButton(
			self.buttons, (222,422), 'yes')
		self.no_btn = PromptButton(
			self.buttons, (544,422), 'no')

	def draw(self):
		self.display_surface.blit(self.check_bg, self.check_bg_rect)
		for text in self.text:
			text.draw(self.display_surface)
		for button in self.buttons:
			button.custom_draw()

	def full_exit(self):
		# if the player has chosen to quit the game completely when 
		# not in a main menu, return true
		if self.exit_type == 'desktop':
			return True
		return False


class SaveCheck(PauseMenu):
	'''
	verifies that the user definitely wants to save their game
	'''
	def __init__(self,menu_type=None):
		super().__init__(menu_type)

	def create_self(self,menu_type):
		self.type = 'saving'

		self.check_bg = pygame.image.load(
			'graphics/ui/backgrounds/check_screen.png').convert_alpha()
		self.check_bg_rect = self.check_bg.get_rect(center=(MID_W,MID_H))
		self.text = []
		self.text.append(Text('save your',
			(MID_W, MID_H - 90), 
			TEXT_M, CYAN))
		self.text.append(Text('current progress?',
			(MID_W, MID_H - 26), 
			TEXT_M, CYAN))

		self.buttons = pygame.sprite.Group()
		self.yes_btn = PromptButton(
			self.buttons, (222,422), 'yes')
		self.no_btn = PromptButton(
			self.buttons, (544,422), 'no')
		
	def draw(self):
		self.display_surface.blit(self.check_bg, self.check_bg_rect)
		for text in self.text:
			text.draw(self.display_surface)
		for button in self.buttons:
			button.custom_draw()