import pygame
import sys

from settings import *
from states import TitleState, MainMenuState, NewGameCheckState, LoadSaveState, DeleteSaveState, TutorialState, ForestState, DungeonState, GameOverState
from pause_menu import Stats
from player_store import TempStore

class Game:
	'''
	controls the main game loop (keeps the game running)
	'''
	def __init__(self, states, start_state):
		# general setup + initialisation
		pygame.init()
		pygame.display.set_caption('game')
		self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT), vsync=1)
		self.clock = pygame.time.Clock()
		self.running = True
		self.paused = False
		pygame.mouse.set_visible(False)
		self.data_store = TempStore()

		# state initialisation
		self.states = states
		self.state_label = start_state
		self.state = self.states[self.state_label]
		self.state.new()

	def change_state(self):
		# handles the change from one state to another
		
		try: # carrying over player data between states
			if self.state.next != 'game_over':
				self.state.player.export_stats()
		except:
			if self.state.next != 'forest' and self.state.next != 'delete' and self.state.next != 'tutorial':
				# player data cleared when outside of the if condition's specified states
				self.data_store = TempStore()

		# resetting for next change
		self.state.done = False
		self.paused = False
		pygame.mouse.set_visible(False)

		# flips state and initialises it
		self.state_label = self.state.next
		self.state.reset_next()
		self.state = self.states[self.state_label]
		self.state.new(self.data_store)
		
	def event_loop(self):
		# main event loop, only handles quitting and opening the menu
		# other events passed to current state event handler

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False

			# can only pause in dungeon and forest; no need to pause in menus
			if event.type == pygame.KEYDOWN and (
				self.state_label == 'forest' or self.state_label == 'dungeon'):
				
				# flips pause state every time escape key is pressed 
				# (when in one of the above areas)
				if event.key == pygame.K_ESCAPE:
					self.paused = not self.paused
					self.state.menu = Stats(self.state.player)
					pygame.mouse.set_visible(self.paused)

			# passes the player's current data, the currently queued event, and the pause status
			# to the current state's event handler
			self.state.event_handler(event, self.data_store, self.paused)

	def update(self):
		# updates each state / calls state's updater
		if self.state.quit:
			self.running = False
		elif self.state.done:
			self.change_state()

		if not self.paused:
			# if player not in pause menu, game continues to update 
			# (enemies move, player can move, etc.)
			self.state.update()
		else:
			# if player is in the pause menu, separate state update method called
			# so that game is not updating outside of the menu (appearing to be paused)
			self.state.paused()

	def main(self):
		# main loop
		while self.running:
			self.clock.tick(FPS)
			self.screen.fill(CYAN)
			self.event_loop()
			self.update()
			pygame.display.update()

# the various states that the game can be in
STATES = {
	'title'		: TitleState(),
	'menu'		: MainMenuState(),
	'new_check' : NewGameCheckState(),
	'saves'		: LoadSaveState(),
	'delete'	: DeleteSaveState(),
	'tutorial'	: TutorialState(),
	'forest'	: ForestState(),
	'dungeon'	: DungeonState(),
	'game_over'	: GameOverState()}

# runs the game
game = Game(STATES, 'title') # first screen user sees is the title screen
game.main()
pygame.quit()
sys.exit()