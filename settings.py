import pygame
from os import listdir
from os.path import join

# visual/display values
FPS = 60
SCREEN_WIDTH = 1024
MID_W = 512
SCREEN_HEIGHT = 720
MID_H = 360
TILE_SIZE = 32

# map creation values
MAP_WIDTH = 64
MAP_HEIGHT = 56
LAYERS = { 				# map layers for visual layering of graphics
	'background': 0,
	'floor': 1,
	'mid_layer': 2,
	'main': 3,
	'foreground': 4}

# colours
WHITE = (238,238,238)
CYAN = (30,92,100)
BLACK = (18,22,47)
RED = (185,41,75)
HP_COL = (232,88,138)
STAMINA_COL = (89,209,152)
ATK_COL = (93,210,205)
MANA_COL = (143,92,248)

# text settings
UI_FONT = 'graphics/font/Pixellari.ttf'
TEXT_L = 96
TEXT_M = 64
TEXT_S = 32
TEXT_XS = 22

# tile values mapped to corresponding tile positions on tilesheet 
# (stored in graphics folder)
TILE_VALUES = {'2':[5,6], '8':[6,6], '10':[8,5], 
'11':[7,5], '16':[4,6], '18':[2,6], '22':[1,6], 
'24':[2,5], '26':[8,4], '27':[7,4], '30':[6,4], 
'31':[5,4], '64':[3,6], '66':[1,5], '72':[6,5], 
'74':[4,4], '75':[2,4], '80':[4,5], '82':[4,3], 
'84':[4,5], '86':[3,3], '88':[8,3], '90':[8,2], 
'91':[7,2], '94':[6,2], '95':[5,2], '104':[5,5], 
'106':[3,4], '107':[1,4], '120':[6,3], '122':[8,1], 
'123':[7,1], '126':[6,1], '127':[5,1], '150':[1,3], 
'200':[6,5], '208':[3,5], '210':[2,3], '214':[1,3], 
'216':[7,3], '218':[4,2], '219':[3,2], '222':[2,2], 
'223':[1,2], '243':[2,3], '248':[5,3], '250':[4,1], 
'251':[3,1], '254':[2,1], '255':[3,7], '0':[7,6], 
'X':[5,7], 'F':[4,7], 'plain':[1,7], 'edge':[2,7],
'floor':[1,1]}

# player values
DASH_STAMINA = 15 		# how much stamina a dash consumes
MAGIC_MANA = 50 		# how much mana a magic attack consumes
MAGIC_DMG = 25 			# magic attack does more damage

# enemy values
ENEMY = {
'health': 80, 			# how much health enemy has
'attack': 5, 			# how much damage enemy does to player
'speed': 3, 			# enemy movement speed
'attack radius': 60, 	# when within this distance from the player, enemy will attack
'caution radius': 300}	# when within this distance from the player, enemy will follow player
AOE_FADE_VAL = 255 / 43


def import_folder(path):
	# imports images for each animation, returns them as a list of surfaces
	surf_list = []
	for img in listdir(path):
		full_path = join(path, img)
		img_surf = pygame.image.load(full_path).convert_alpha()
		surf_list.append(img_surf)
	return surf_list


class Text:
	'''
	creates and renders text when text object instantiated
	'''
	def __init__(self,text,pos,text_size,colour,alpha=False):
		self.font = pygame.font.Font(UI_FONT, text_size)
		self.text_surf = self.font.render(text, False, colour)
		self.text_rect = self.text_surf.get_rect(center=pos)
		if alpha:
			self.text_surf.set_colorkey(CYAN)
			self.alpha = 0

	def draw(self, surface):
		surface.blit(self.text_surf, self.text_rect)

	def update_alpha(self):
		# used for fading text
		self.alpha += 3
		self.text_surf.set_alpha(self.alpha)