import pygame

from settings import *
from dun_gen import get_dungeon
from sprites import Tile, TileSheet, ExamplePlayer, Player, Enemy
from camera import ForestCameraGroup, DungeonCameraGroup
from pause_menu import Stats, General, Check, SaveCheck, UpgradeCheck, NoUpgrade
from buttons import Tab, GenButton, PromptButton, MainMenuButton, SaveButton, SmallButton
from attacks import Sword, Magic
from overlay import Overlay, TextBubble

class State:
	'''
	base class for states
	'''
	def __init__(self):
		self.done = False			# moving to next scene
		self.quit = False			# quit to desktop
		self.next = None			# next scene in sequence
		self.mouse_visible = False 	# mouse visible only when paused


class TitleState(State):
	'''
	intro state - first screen user sees when opening the game
	'''
	def __init__(self):
		super().__init__()
		self.next = 'menu'

	def reset_next(self):
		# resets the next state in the sequence
		self.next = 'menu'

	def new(self, data_store=None):
		# initialises creation of the state
		self.display_surface = pygame.display.get_surface()
		self.text = Text('press any button to start',
			(MID_W, MID_H), 
			TEXT_M, WHITE, alpha=True)

	def update(self):
		# state updater
		self.text.update_alpha()
		self.text.draw(self.display_surface)

	def event_handler(self, event, data_store=None, paused=False):
		# if user presses any button before the text is done fading in, the text
		# goes opaque (meaning they can then get to the main menu screen)
		if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
			if self.text.alpha < 255:
				self.text.alpha = 255
			else:
				self.done = True


class MainMenuState(State):
	'''
	main menu - user can start a new game, 
	load a save (given they have save data), or exit the game
	'''
	def __init__(self):
		super().__init__()
		self.next = 'tutorial'
		self.screen = None

	def reset_next(self):
		self.next = 'tutorial'

	def new(self, data_store):
		self.display_surface = pygame.display.get_surface()
		self.mouse_visible = True
		pygame.mouse.set_visible(self.mouse_visible)

		self.buttons = pygame.sprite.Group()
		self.check_for_saves(data_store)
		self.create_btns()	

	def check_for_saves(self, data_store):
		# changes type of menu to be displayed based on if user has save data
		if data_store.check_for_saves():
			# user has save data, main menu will have load game option
			self.screen = 'saves'
		else:
			# user has no save data, main menu will not have load game option
			self.screen = 'no_saves'

	def create_btns(self):
		# creates the menu buttons
		self.new_game = MainMenuButton(
			self.buttons, (MID_W, MID_H - 100), 'new game')
		self.exit_desktop = MainMenuButton(
			self.buttons, (MID_W, MID_H + 100), 'exit to desktop')
		if self.screen == 'saves':
			self.load_game = MainMenuButton(
				self.buttons, (MID_W,MID_H), 'load game')

	def update(self):
		self.display_surface.fill(CYAN)
		for button in self.buttons:
			button.custom_draw()

	def event_handler(self, event, data_store, paused=False):
		mouse_pos = pygame.mouse.get_pos()
		if event.type == pygame.MOUSEBUTTONDOWN:

			if self.screen == 'saves':
				if self.new_game.on_click(mouse_pos):
					self.next = 'new_check'
					self.done = True
				if self.load_game.on_click(mouse_pos):
					self.next = 'saves'
					self.done = True
				if self.exit_desktop.on_click(mouse_pos):
					self.quit = True
			else:
				if self.new_game.on_click(mouse_pos):
					data_store.create_new_save('1')
					self.done = True
				if self.exit_desktop.on_click(mouse_pos):
					self.quit = True

		for button in self.buttons:
			button.on_hover(mouse_pos)


class NewGameCheckState(State):
	'''
	checks if user wants to start a new game
	'''
	def __init__(self):
		super().__init__()
		self.next = 'tutorial'

	def reset_next(self):
		self.next = 'tutorial'

	def new(self, data_store):
		self.display_surface = pygame.display.get_surface()
		self.mouse_visible = True
		pygame.mouse.set_visible(self.mouse_visible)

		self.buttons = pygame.sprite.Group()
		self.used_slots = data_store.count_used_slots()
		self.create_btns()
		self.create_text()

	def create_btns(self):
		if self.used_slots == 3:
			# user told they have to delete a save in order to start a new game,
			# can only accept and be returned to menu (to delete save if they wish)
			self.ok_btn = PromptButton(self.buttons, (384,510), 'ok')
		else:
			self.yes_btn = PromptButton(
				self.buttons, (222,510), 'yes')
			self.no_btn = PromptButton(
				self.buttons, (544,510), 'no')

	def create_text(self):
		self.text = []

		if self.used_slots < 3:
			# save slots available
			self.text.append(Text('are you sure you want', 
				(MID_W, MID_H - 84), 
				TEXT_M, WHITE))
			self.text.append(Text('to create a new save?', 
				(MID_W, MID_H), 
				TEXT_M, WHITE))
		else:
			# no save slots available
			self.text.append(Text('no save slots remaining.', 
				(MID_W, MID_H - 144), 
				TEXT_M, WHITE))
			self.text.append(Text('delete a previous save', 
				(MID_W, MID_H - 60), 
				TEXT_M, WHITE))
			self.text.append(Text('to begin a new game.', 
				(MID_W, MID_H + 24), 
				TEXT_M, WHITE))

	def update(self):
		self.display_surface.fill(CYAN)
		for text in self.text:
			text.draw(self.display_surface)
		for button in self.buttons:
			button.custom_draw()

	def event_handler(self, event, data_store, paused=False):
		mouse_pos = pygame.mouse.get_pos()
		if event.type == pygame.MOUSEBUTTONDOWN:

			if self.used_slots < 3:
				# save slots available
				if self.yes_btn.on_click(mouse_pos):
					data_store.create_new_save(str(self.used_slots + 1))
					self.done = True
				if self.no_btn.on_click(mouse_pos):
					self.next = 'menu'
					self.done = True
			else:
				# no save slots available
				if self.ok_btn.on_click(mouse_pos):
					self.next = 'menu'
					self.done = True

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				self.next = 'menu'
				self.done = True

		for button in self.buttons:
			button.on_hover(mouse_pos)


class LoadSaveState(State):
	'''
	displays possible saves that the user can load
	'''
	def __init__(self):
		super().__init__()
		self.next = 'forest'

	def reset_next(self):
		self.next = 'forest'

	def new(self, data_store):
		self.display_surface = pygame.display.get_surface()
		self.mouse_visible = True
		pygame.mouse.set_visible(self.mouse_visible)

		self.bg = pygame.image.load('graphics/ui/backgrounds/save_load.png').convert()
		self.bg_rect = self.bg.get_rect()

		self.buttons = pygame.sprite.Group()
		self.create_btns(data_store)
		self.text = []

	def create_btns(self, data_store):
		self.return_btn = SmallButton(
			self.buttons, (70,70), '<')

		available_saves = data_store.count_used_slots()

		self.s1 = SaveButton(
			self.buttons, (462,220), 'save 1')
		self.s1_delete = SmallButton(
			self.buttons, (662,220), 'X', '1')
		self.slots = 1

		if available_saves > 1:
			self.s2 = SaveButton(
				self.buttons, (462,MID_H), 'save 2')
			self.s2_delete = SmallButton(
				self.buttons, (662,MID_H), 'X', '2')
			self.slots += 1

			if available_saves > 2:
				self.s3 = SaveButton(
					self.buttons, (462,500), 'save 3')
				self.s3_delete = SmallButton(
					self.buttons, (662,500), 'X', '3')
				self.slots += 1

	def event_handler(self, event, data_store, paused=False):
		mouse_pos = pygame.mouse.get_pos()
		if event.type == pygame.MOUSEBUTTONDOWN:

			if self.s1.on_click(mouse_pos):
				self.done = True
			if self.s1_delete.on_click(mouse_pos):
				self.next = 'delete'
				self.done = True

			if self.slots > 1:
				if self.s2.on_click(mouse_pos):
					self.done = True
				if self.s2_delete.on_click(mouse_pos):
					self.next = 'delete'
					self.done = True

				if self.slots > 2:
					if self.s3.on_click(mouse_pos):
						self.done = True
					if self.s3_delete.on_click(mouse_pos):
						self.next = 'delete'
						self.done = True

			if self.return_btn.on_click(mouse_pos):
				self.next = 'menu'
				self.done = True	

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				self.next = 'menu'
				self.done = True

		for button in self.buttons:
			if button.on_hover(mouse_pos) and button.hover_data:
				data_store.import_save(button.hover_data)
				self.display_save_info(data_store)

	def display_save_info(self, data_store):
		# displays most recently hovered save button's save data on screen

		self.text = []
		self.text.append(Text('save slot ' + data_store.save_slot + ': ', 
			(170,650), 
			TEXT_S, WHITE))
		self.text.append(Text('dungeons completed: ' + str(
			data_store.save_data['dungeons']), 
			(MID_W,650), 
			TEXT_S, WHITE))
		self.text.append(Text('wisps: ' + str(data_store.save_data['wisps']), 
			(854,650), 
			TEXT_S, WHITE))

	def update(self):
		self.display_surface.blit(self.bg,self.bg_rect)
		for text in self.text:
			text.draw(self.display_surface)
		for button in self.buttons:
			button.custom_draw()


class DeleteSaveState(State):
	'''
	user asked if they actually want to delete the selected save
	'''
	def __init__(self):
		super().__init__()
		self.next = 'saves'

	def reset_next(self):
		self.next = 'saves'

	def new(self, data_store):
		self.display_surface = pygame.display.get_surface()
		self.mouse_visible = True
		pygame.mouse.set_visible(self.mouse_visible)

		self.buttons = pygame.sprite.Group() 
		self.create_btns()
		self.create_text()

		self.used_slots = data_store.count_used_slots()

	def create_btns(self):
		self.yes_btn = PromptButton(
			self.buttons, (222,510), 'yes')
		self.no_btn = PromptButton(
			self.buttons, (544,510), 'no')

	def create_text(self):
		self.text = []
		self.text.append(Text('are you sure you want', 
			(MID_W, MID_H - 94), 
			TEXT_M, WHITE))
		self.text.append(Text('to delete this save?', 
			(MID_W, MID_H - 10), 
			TEXT_M, WHITE))
		self.text.append(Text('this cannot be undone.', 
			(MID_W, MID_H + 70), 
			TEXT_S, WHITE))

	def event_handler(self, event, data_store, paused=False):
		mouse_pos = pygame.mouse.get_pos()
		if event.type == pygame.MOUSEBUTTONDOWN:

			if self.yes_btn.on_click(mouse_pos):
				# checks if deleting a save
				data_store.delete_save(self.used_slots)
				if self.used_slots == 1:
					self.next = 'menu'
				self.done = True
			if self.no_btn.on_click(mouse_pos):
				# not deleting save
				self.done = True

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				self.done = True

		for button in self.buttons:
			button.on_hover(mouse_pos)

	def update(self):
		self.display_surface.fill(CYAN)
		for text in self.text:
			text.draw(self.display_surface)
		for button in self.buttons:
			button.custom_draw()


class TutorialState(State):
	'''
	user led through a few tutorial screens describing how to play the game
	'''
	def __init__(self):
		super().__init__()
		self.next = 'forest'
		self.screen = 'new'

	def reset_next(self):
		self.screen = 'new'
		self.next = 'forest'

	def new(self, data_store):
		self.display_surface = pygame.display.get_surface()
		self.mouse_visible = True
		pygame.mouse.set_visible(self.mouse_visible)

		self.buttons = pygame.sprite.Group()
		self.ok_btn = PromptButton(self.buttons, (384,630), 'ok') 

		self.clean_screen('new')

	def magic_atk(self):
		# needed so that magic attack can actually be displayed on screen
		self.current_atk = Magic(self.magic_example, self.atk_sprites)

	def destroy_atk(self):
		# magic attack is its own sprite, removed once attack example complete
		if self.current_atk:
			self.current_atk.kill()
		self.current_atk = None

	def clean_screen(self,screen):
		# clears tutorial screen data when next tutorial page is moved onto
		self.text = []
		self.all_sprites = pygame.sprite.Group()
		self.screen = screen
		self.bg = pygame.image.load('graphics/ui/backgrounds/intro_' + screen + '.png').convert()
		self.bg_rect = self.bg.get_rect()

	def explain_inputs(self):
		# screen explaining how the user can perform moves and attacks
		self.clean_screen('inputs')

		self.atk_sprites = pygame.sprite.Group()

		# 4 sprites resembling the player's own, which show the various moves and
		# cannot be interacted with / controlled by player
		self.move_example = ExamplePlayer((115,300), 
			self.all_sprites, 'move', self.magic_atk, self.destroy_atk)
		self.sword_example = ExamplePlayer((358,300), 
			self.all_sprites, 'sword', self.magic_atk, self.destroy_atk)
		self.magic_example = ExamplePlayer((602,300), 
			self.all_sprites, 'magic', self.magic_atk, self.destroy_atk)
		self.dash_example = ExamplePlayer((845,300), 
			self.all_sprites, 'dash', self.magic_atk, self.destroy_atk)

		# neatens edges surrounding magic attack
		self.overlap = pygame.image.load('graphics/ui/inputs_overlap.png').convert_alpha()
		self.overlap_rect = self.overlap.get_rect(topleft=(534,240))

	def explain_stats(self):
		# screen explaining stats in the game and the stats menu
		self.clean_screen('stats')

	def explain_general(self):
		# screen explaining the pause menu's general section
		self.clean_screen('gen')

	def final(self):
		# screen explaining other miscellaneous game things
		self.clean_screen('final')

	def update(self):
		self.display_surface.blit(self.bg, self.bg_rect)

		if self.screen == 'inputs':
			if self.atk_sprites:
				for atk in self.atk_sprites:
					atk.update_atk(self.magic_example, True)
					self.atk_sprites.draw(self.display_surface)
			self.all_sprites.update()
			self.all_sprites.draw(self.display_surface)
			self.display_surface.blit(self.overlap, self.overlap_rect)

		for text in self.text:
			text.draw(self.display_surface)
		for button in self.buttons:
			button.custom_draw()

	def event_handler(self, event, data_store=None, paused=None):
		mouse_pos = pygame.mouse.get_pos()
		if event.type == pygame.MOUSEBUTTONDOWN:

			if self.ok_btn.on_click(mouse_pos):
				if self.screen == 'new':
					self.explain_inputs()
				elif self.screen == 'inputs':
					self.explain_stats()
				elif self.screen == 'stats':
					self.explain_general()
				elif self.screen == 'gen':
					self.final()
				elif self.screen == 'final':
					self.done = True

		for button in self.buttons:
			button.on_hover(mouse_pos)


class ForestState(State):
	'''
	the first place that the player loads into where they can actually 
	see and control their character. no enemies spawn here, and the player
	can enter the dungeon in this area. as well as that, they are able to 
	save their game progress here
	'''
	def __init__(self):
		super().__init__()
		self.next = 'dungeon'

	def reset_next(self):
		self.next = 'dungeon'

	def new(self, data_store):
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = ForestCameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.interact_sprites = pygame.sprite.Group()
		self.atk_sprites = pygame.sprite.Group()

		# creates tile to enter dungeon
		Tile(
			pos=(SCREEN_WIDTH//2, 351),
			surface=pygame.image.load('graphics/level/entertile.png').convert_alpha(),
			groups=(self.all_sprites, self.interact_sprites),
			depth=LAYERS['floor'])

		# player instantiation
		self.player = Player((740,400), self.all_sprites, self.collision_sprites, 
			self.create_atk, self.destroy_atk, data_store, self.stamina_warning)

		# menu and overlays
		self.text = []
		self.menu = Stats(self.player)
		self.overlay = Overlay(self.player)
		self.enter_bubble = TextBubble('enter dungeon?')
		self.draw_bubble = False
		self.stamina_bubble = TextBubble('tired')
		self.draw_stam_bubble = False

	def create_atk(self, type):
		# sprite which, on collision with an enemy hitbox, makes the enemy take damage
		# not needed for this state as there are no enemies, but player may still want to practice
		if type == 'magic':
			self.current_atk = Magic(self.player, [self.all_sprites, self.atk_sprites])
		else:
			self.current_atk = None

	def destroy_atk(self):
		# destroys sprite attack once performed
		if self.current_atk:
			self.current_atk.kill()
		self.current_atk = None

	def atk_logic(self):
		# basic attack logic - only need to move attack with player movement, 
		# no enemies to kill in forest
		if self.current_atk:
			self.current_atk.update_atk(self.player)

	def display_cost(self,type):
		# displays cost to upgrade currently hovered stat on screen in the menu
		self.text = []
		self.text.append(Text('upgrade', 
			(MID_W,430), 
			TEXT_S, WHITE))
		self.text.append(Text('cost:', 
			(MID_W,460), 
			TEXT_S, WHITE))
		self.text.append(Text(str(self.player.upgrade[type][1]), 
			(MID_W,510), 
			TEXT_M, WHITE))

	def upgrade_check(self,type):
		# checks if the user can actually upgrade the chosen stat
		if self.player.stats[type] < self.player.max_stats[type]:
			if self.player.stats['wisps'] >= self.player.upgrade[type][1]:
				return False
			error = 'cost'
			# cannot afford to upgrade
			return error
		error = 'full'
		# stat is already fully upgraded
		return error

	def get_upgrade(self,type):
		# upgrades the player's stat and refreshes the overlay to reflect this change
		self.player.stats['wisps'] -= self.player.upgrade[type][1]
		self.player.stats[type] += self.player.upgrade[type][0]
		self.overlay = Overlay(self.player)

	def stamina_warning(self,type):
		# if user does not have enough stamina to dash, small bubble appears
		# above player's head until enough stamina is regained to be able to 
		# perform the move
		if type == 'check':
			if self.player.stamina >= DASH_STAMINA:
				self.draw_stam_bubble = False
		if self.player.stamina < DASH_STAMINA:
			if type == 'on_press':
				self.draw_stam_bubble = True

	def update(self):
		# updater for when game is unpaused
		self.all_sprites.update()
		self.all_sprites.custom_draw(self.player)
		self.atk_logic()

		# overlay updates
		self.overlay.display(self.player)
		if self.draw_bubble:
			self.enter_bubble.custom_draw(self.player)
		if self.draw_stam_bubble:
			self.stamina_bubble.custom_draw(self.player)

	def paused(self):
		# updater for when game is paused
		self.all_sprites.custom_draw(self.player)
		self.menu.draw_menu()
		self.menu.display(self.player)
		self.overlay.display(self.player)

		# menu text updater
		if self.displaying_cost:
			self.display_cost(self.displaying_cost)
		else:
			self.text = []
		for text in self.text:
			text.draw(self.display_surface)

	def event_handler(self, event, data_store, paused):
		# separate event handlers for if the game is paused or unpaused
		# (neatens appearance of methods)
		if not paused:
			self.game_events(event)
		else:
			self.paused_events(event, data_store)

	def game_events(self, event):
		# events when game is unpaused
		keys = pygame.key.get_pressed()
		if pygame.sprite.spritecollide(self.player, self.interact_sprites, False):
			self.draw_bubble = True
			if keys[pygame.K_f]:
				self.done = True
		else:
			self.draw_bubble = False

	def paused_events(self, event, data_store):
		# events when game is paused
		mouse_pos = pygame.mouse.get_pos()
		if event.type == pygame.MOUSEBUTTONDOWN:
				
			# in the stats section of the menu
			if self.menu.type == 'stats':	
				if self.menu.general_tab.on_click(mouse_pos):
					self.menu = General('forest')
				else:
					for upgrade in self.menu.upgrade_btns:
						if upgrade.on_click(mouse_pos):
							self.displaying_cost = False
							check = self.upgrade_check(upgrade.type)
							if check:
								self.menu = NoUpgrade(check)
							else:
								self.menu = UpgradeCheck(upgrade.type)

			# in the general section of the menu
			elif self.menu.type == 'general':
				if self.menu.stats_tab.on_click(mouse_pos):
					self.menu = Stats(self.player)
				elif self.menu.save_game.on_click(mouse_pos):
					self.menu = SaveCheck()
				elif self.menu.main_menu.on_click(mouse_pos):
					self.menu = Check('main_menu')
				elif self.menu.exit_desktop.on_click(mouse_pos):
					self.menu = Check('desktop')

			# game seeing if user definitely wants to quit
			elif self.menu.type == 'check':
				if self.menu.yes_btn.on_click(mouse_pos):
					if self.menu.full_exit():
						self.quit = True
					else:
						self.next = 'menu'
						self.done = True
				elif self.menu.no_btn.on_click(mouse_pos):
					self.menu = General('forest')

			# game seeing if user definitely wants to save their current progress
			elif self.menu.type == 'saving':
				if self.menu.yes_btn.on_click(mouse_pos):
					data_store.update_current(self.player.stats)
					data_store.write_to_save()
					self.menu = General('forest')
				elif self.menu.no_btn.on_click(mouse_pos):
					self.menu = General('forest')

			# menu lets user know that a stats upgrade cannot be made
			elif self.menu.type == 'no_upgrade_full' or self.menu.type == 'no_upgrade_cost':
				if self.menu.ok_btn.on_click(mouse_pos):
					self.menu = Stats(self.player)
	
			# checking if user definitely wants to upgrade stat
			else:	
				if self.menu.yes_btn.on_click(mouse_pos):
					self.get_upgrade(self.menu.type)
					self.menu = Stats(self.player)
				elif self.menu.no_btn.on_click(mouse_pos):
					self.menu = Stats(self.player)

		for button in self.menu.buttons:
			button.on_hover(mouse_pos)

		if self.menu.type == 'stats':
			for button in self.menu.upgrade_btns:
				if button.on_hover(mouse_pos) and button.hover_data:
					if self.player.stats[button.hover_data] < self.player.max_stats[button.hover_data]:
						self.displaying_cost = button.hover_data
						break # break out of for loop if stat is being hovered over
			else:
				self.displaying_cost = False


class DungeonState(State):
	'''
	where the majority of the gameplay takes place. generates random dungeon layout
	upon entering each time. user is not able to save in here, and they must exit through
	the exit point to keep their items from this current dungeon runthrough.
	'''
	def __init__(self):
		super().__init__()
		self.next = 'forest'

	def reset_next(self):
		self.next = 'forest'

	def new(self, data_store):
		self.display_surface = pygame.display.get_surface()
		self.bg_rect = pygame.Rect((0,0), (SCREEN_WIDTH,SCREEN_HEIGHT))

		# sprite groups
		self.all_sprites = DungeonCameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.enemy_collision_sprites = pygame.sprite.Group()
		self.interact_sprites = pygame.sprite.Group()
		self.atk_sprites = pygame.sprite.Group()
		self.killable_sprites = pygame.sprite.Group()

		# generates dungeon and gets required tiles
		self.tile_set = TileSheet('graphics/level/tiles.png')
		self.generate_dungeon()

		# generates player and sets spawn position
		pos_x = self.dungeon.player_spawn[0] * TILE_SIZE
		pos_y = self.dungeon.player_spawn[1] * TILE_SIZE
		self.player = Player((pos_x, pos_y - TILE_SIZE), 
			self.all_sprites, self.collision_sprites, 
			self.create_atk, self.destroy_atk, 
			data_store, self.stamina_warning)
		self.current_atk = None

		# menu and overlay
		self.menu = Stats(self.player)
		self.overlay = Overlay(self.player)
		self.exit_bubbles = []
		self.exit_bubbles.append(
			TextBubble('leave dungeon?'))
		self.exit_bubbles.append(
			TextBubble(("you won't be able to return."), pos=(545,350)))
		self.draw_exit_bubble = False
		self.stamina_bubble = TextBubble('tired')
		self.draw_stam_bubble = False

	def generate_dungeon(self):
		# generates tilemap by calling get_dungeon function (from dun_gen),
		# and then uses that to blit tiles to the screen
		self.dungeon = get_dungeon()

		# map layer 1
		for row_coord, row in enumerate(self.dungeon.tilemap):
			for col_coord, col in enumerate(row):
				x = col_coord * TILE_SIZE
				y = row_coord * TILE_SIZE

				# wall tile
				if isinstance(col,int):
					if col <= 31:
						image = self.tile_set.get_image(TILE_VALUES['edge'])
					else:
						image = self.tile_set.get_image(TILE_VALUES['plain'])
					Tile(
						pos=(x, y),
						surface=image,
						groups=(self.all_sprites,self.collision_sprites),
						type='wall')

				# corridor tiles (floor but in enemy col group for enemy collision purposes)
				elif col[0] == 'c':
					image = self.tile_set.get_image(TILE_VALUES['floor'])
					Tile(
						pos=(x, y),
						surface=image,
						groups=(self.all_sprites,self.enemy_collision_sprites),
						depth=LAYERS['floor'],
						type='corridor')

				# floor tiles
				else:
					if col[0] == '.':
						image = self.tile_set.get_image(TILE_VALUES['floor'])
					elif col[0] == 'D':
						sheet_pos = TILE_VALUES[col[1:]]
						image = self.tile_set.get_image(sheet_pos)
					Tile(
						pos=(x, y),
						surface=image,
						groups=self.all_sprites,
						depth=LAYERS['floor'],
						type='floor')

		# so enemies can't walk through walls OR in corridors
		self.enemy_collision_sprites.add(self.collision_sprites)

		# map layer 2
		for row_coord, row in enumerate(self.dungeon.tilemap_overlay):
			for col_coord, col in enumerate(row):
				x = col_coord * TILE_SIZE
				y = row_coord * TILE_SIZE

				# enemies
				if col == 'M':
					Enemy(
						pos=(x,y),
						groups=[self.all_sprites,self.killable_sprites],
						collision_sprites=self.enemy_collision_sprites,
						all_sprites=self.all_sprites,
						dmg_player=self.dmg_player,
						heal_player=self.heal_player,
						add_wisps=self.add_wisps)	

				# exit point
				elif col == 'X':
					image = self.tile_set.get_image(TILE_VALUES[col])
					Tile(
						pos=(x, y),
						surface=image,
						groups=[self.all_sprites,self.interact_sprites],
						depth=LAYERS['mid_layer'],
						type='interact')

				# flowers
				elif col == 'F':
					image = self.tile_set.get_image(TILE_VALUES[col])
					Tile(
						pos=(x, y),
						surface=image,
						groups=[self.all_sprites,self.killable_sprites],
						depth=LAYERS['mid_layer'],
						type='flowers')

	def create_atk(self, type):
		# sprite which, on collision with an enemy hitbox, makes the enemy take damage
		if type == 'sword':
			self.current_atk = Sword(self.player, self.atk_sprites)
		else:
			self.current_atk = Magic(self.player, [self.all_sprites, self.atk_sprites])

	def destroy_atk(self):
		# destroys sprite attack once performed
		if self.current_atk:
			self.current_atk.kill()
		self.current_atk = None

	def atk_logic(self):
		# more complex attack logic
		if self.current_atk:
			self.current_atk.update_atk(self.player)
			hit_sprites = pygame.sprite.spritecollide(self.current_atk,self.killable_sprites,False)
			for sprite in hit_sprites:
				if sprite.type == 'flowers':
					# nearby flowers destroyed when player performs an attack
					sprite.kill()
				else:
					# enemies take damage
					sprite.get_hurt(self.player, self.current_atk.type)

	def dmg_player(self):
		# called when enemy attack hits player
		if self.player.vulnerable and not self.player.dashing:
			self.player.health -= ENEMY['attack']
			self.player.vulnerable = False
			self.player.hit_time = pygame.time.get_ticks()
			# player can't keep repeatedly taking damage within certain amount of time
			# (gets recovery time)

	def heal_player(self):
		# player health regens partially upon killing an enemy
		if self.player.health + 15 > self.player.stats['health']:
			self.player.health = self.player.stats['health']
		else:
			self.player.health += 15

	def check_death(self):
		# checks if player has died (if their hp has hit 0 or below)
		if self.player.health <= 0:
			self.done = True
			self.next = 'game_over'

	def add_wisps(self):
		# if player defeats an enemy, they receive points in return
		self.player.stats['wisps'] += 2

	def stamina_warning(self, type):
		if type == 'check':
			if self.player.stamina >= DASH_STAMINA:
				self.draw_stam_bubble = False
		if self.player.stamina < DASH_STAMINA:
			if type == 'on_press':
				self.draw_stam_bubble = True

	def display_cost(self, type):
		self.text = []
		self.text.append(Text('upgrade', 
			(MID_W,430), 
			TEXT_S, WHITE))
		self.text.append(Text('cost:', 
			(MID_W,460), 
			TEXT_S, WHITE))
		self.text.append(Text(str(self.player.upgrade[type][1]), 
			(MID_W,510), 
			TEXT_M, WHITE))

	def upgrade_check(self, type):
		if self.player.stats[type] < self.player.max_stats[type]:
			if self.player.stats['wisps'] >= self.player.upgrade[type][1]:
				return False
			return 'cost'
		return 'full'

	def get_upgrade(self, type):
		self.player.stats['wisps'] -= self.player.upgrade[type][1]
		self.player.stats[type] += self.player.upgrade[type][0]
		self.overlay = Overlay(self.player)

	def update(self):
		self.display_surface.fill(CYAN)

		self.all_sprites.custom_draw(self.player)
		self.all_sprites.update()
		self.all_sprites.enemy_update(self.player)
		self.atk_logic()
		self.check_death()

		self.overlay.display(self.player)
		if self.draw_exit_bubble:
			for bubble in self.exit_bubbles:
				bubble.custom_draw()
		if self.draw_stam_bubble:
			self.stamina_bubble.custom_draw()

	def event_handler(self, event, data_store, paused):
		if not paused:
			self.game_events(event)
		else:
			self.paused_events(event, data_store)

	def game_events(self, event):
		keys = pygame.key.get_pressed()
		if pygame.sprite.spritecollide(self.player, self.interact_sprites, False):
			self.draw_exit_bubble = True
			if keys[pygame.K_f] and event.type == pygame.KEYDOWN:
				# keydown so that dungeon count only goes up by 1
				self.done = True
				self.player.stats['dungeons'] += 1
		else:
			self.draw_exit_bubble = False

	def paused_events(self, event, data_store):
		# largely similar to forest state's event handler, but instead has specific menus
		# for the dungeon state (rather than specific forest menus)

		mouse_pos = pygame.mouse.get_pos()
		if event.type == pygame.MOUSEBUTTONDOWN:

			if self.menu.type == 'stats':	
				if self.menu.general_tab.on_click(mouse_pos):
					self.menu = General('dungeon')
				else:
					for upgrade in self.menu.upgrade_btns:
						if upgrade.on_click(mouse_pos):
							self.displaying_cost = False
							check = self.upgrade_check(upgrade.type)
							if check:
								self.menu = NoUpgrade(check)
							else:
								self.menu = UpgradeCheck(upgrade.type)

			elif self.menu.type == 'general':
				if self.menu.stats_tab.on_click(mouse_pos):
					self.menu = Stats(self.player)
				elif self.menu.leave_dungeon.on_click(mouse_pos):
					self.menu = Check('forest')
				elif self.menu.main_menu.on_click(mouse_pos):
					self.menu = Check('main_menu')
				elif self.menu.exit_desktop.on_click(mouse_pos):
					self.menu = Check('desktop')

			elif self.menu.type == 'check':
				if self.menu.yes_btn.on_click(mouse_pos):
					if self.menu.full_exit():
						self.quit = True
					elif self.menu.exit_type == 'main_menu':
						self.next = 'menu'
						self.done = True
					else:
						self.player.import_stats()
						self.next = 'forest'
						self.done = True
				if self.menu.no_btn.on_click(mouse_pos):
					self.menu = General('dungeon')

			elif self.menu.type == 'no_upgrade_full' or self.menu.type == 'no_upgrade_cost':
				if self.menu.ok_btn.on_click(mouse_pos):
					self.menu = Stats(self.player)
	
			else:
				if self.menu.yes_btn.on_click(mouse_pos):
					self.get_upgrade(self.menu.type)
					self.menu = Stats(self.player)
				elif self.menu.no_btn.on_click(mouse_pos):
					self.menu = Stats(self.player)

		for button in self.menu.buttons:
			button.on_hover(mouse_pos)

		if self.menu.type == 'stats':
			for button in self.menu.upgrade_btns:
				if button.on_hover(mouse_pos) and button.hover_data:
					if self.player.stats[button.hover_data] < self.player.max_stats[button.hover_data]:
						self.displaying_cost = button.hover_data
						break # break out of for loop if stat is being hovered over
			else:
				self.displaying_cost = False

	def paused(self):
		self.display_surface.fill(CYAN)
		self.all_sprites.custom_draw(self.player) 
		self.menu.draw_menu()
		self.menu.display(self.player)
		self.overlay.display(self.player)

		if self.displaying_cost:
			self.display_cost(self.displaying_cost)
		else:
			self.text = []
		for text in self.text:
			text.draw(self.display_surface)


class GameOverState(State):
	'''
	appears when player health reaches 0 - here, they are returned to the forest state
	and lose their progress from the dungeon that they died in
	'''
	def __init__(self):
		super().__init__()
		self.next = 'forest'

	def reset_next(self):
		self.next = 'forest'

	def new(self, data_store=None):
		self.display_surface = pygame.display.get_surface()
		self.fade_text = Text('you died',
			(MID_W, MID_H), 
			TEXT_L, WHITE, alpha = True)
		self.small_text = Text('press any key to return',
			(MID_W, 500),
			TEXT_S, WHITE)

	def update(self):	
		self.display_surface.fill(RED)
		self.fade_text.update_alpha()
		self.fade_text.draw(self.display_surface)
		if self.fade_text.alpha >= 255:
			self.small_text.draw(self.display_surface)

	def event_handler(self, event, data_store=None, paused=False):
		if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
			if self.fade_text.alpha >= 255:
				self.done = True