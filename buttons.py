import pygame

from settings import *

class Button(pygame.sprite.Sprite):
	'''
	base button class
	'''
	def __init__(self,groups):
		super().__init__(groups)
		self.display_surface = pygame.display.get_surface()
		self.hover_data = False

	def set_image(self,path,hover):
		# sets the button's image and its equivalent hover image
		self.image = pygame.image.load(path + '.png').convert_alpha()
		self.temp_image = self.image
		if hover:
			# if the button changes when hovered over, set a different hover image
			self.hover_image = pygame.image.load(path + '_hover.png').convert_alpha()
		else:
			self.hover_image = self.image

	def create_text(self,text,colour,text_size,pos):
		# creates and renders the text for the button
		self.font = pygame.font.Font(UI_FONT, text_size)
		self.text_surf = self.font.render(text, True, colour)
		self.text_rect = self.text_surf.get_rect(center=pos)

	def custom_draw(self):
		# custom draw method to render the text onto the button
		self.display_surface.blit(self.image, self.rect)
		self.display_surface.blit(self.text_surf, self.text_rect)

	def on_click(self, mouse_pos):
		# checks if the mouse is hovering over the button when a mouse click event is received
		if self.rect.collidepoint(mouse_pos):
			return True
		return False

	def on_hover(self, mouse_pos):
		# checks if the mouse is hovering over the button, and changes the button's image accordingly
		if self.rect.collidepoint(mouse_pos):
			self.image = self.hover_image
			return True
		else:
			self.image = self.temp_image
			return False


class Tab(Button):

	# for the pause menu tabs (stats and general)

	def __init__(self,groups,pos,text,type,colour):
		super().__init__(groups)
		name = 'graphics/ui/buttons/tab' + type
		self.set_image(name,False)
		self.rect = self.image.get_rect(topleft=pos)
		self.create_text(text,colour,TEXT_M,self.rect.center)


class GenButton(Button):
	'''
	pause menu general section buttons
	'''
	def __init__(self,groups,pos,text):
		super().__init__(groups)
		self.set_image('graphics/ui/buttons/pause',True)
		self.rect = self.image.get_rect(center=pos)
		self.create_text(text,WHITE,TEXT_M,self.rect.center)
		

class UpgradeButton(Button):
	'''
	pause menu stats section upgrade buttons
	'''
	def __init__(self,groups,pos,text):
		super().__init__(groups)
		self.set_image('graphics/ui/buttons/upgrade',True)
		self.rect = self.image.get_rect(topleft=pos)

		self.text = text
		self.type = text
		self.hover_data = text
		self.create_text(text,WHITE,TEXT_S,(self.rect.centerx,508))

	def on_hover(self,mouse_pos):
		# custom hover, changes button's text colour so text can still be seen when hovering
		if self.rect.collidepoint(mouse_pos):
			self.image = self.hover_image
			self.create_text(self.text,CYAN,TEXT_S,(self.rect.centerx,508))
			return True
		else:
			self.image = self.temp_image
			self.create_text(self.text,WHITE,TEXT_S,(self.rect.centerx,508))
			return False


class MainMenuButton(Button):
	'''
	menu button for most menu states
	'''
	def __init__(self,groups,pos,text):
		super().__init__(groups)
		self.set_image('graphics/ui/buttons/main',True)
		self.rect = self.image.get_rect(center=pos)
		self.hover_data = text[-1]
		self.create_text(text,WHITE,TEXT_M,self.rect.center)


class SaveButton(Button):
	'''
	specific button used in load saves menu for each save
	'''
	def __init__(self,groups,pos,text):
		super().__init__(groups)
		self.set_image('graphics/ui/buttons/save',True)
		self.rect = self.image.get_rect(center=pos)
		self.hover_data = text[-1]
		self.create_text(text,WHITE,TEXT_M,self.rect.center)


class SmallButton(Button):
	'''
	small square button used in load save menu
	for returning to main menu and deleting a save
	'''
	def __init__(self,groups,pos,text,type=None):
		super().__init__(groups)
		self.set_image('graphics/ui/buttons/delete',True)
		self.rect = self.image.get_rect(center=pos)
		self.hover_data = type
		self.create_text(text,WHITE,TEXT_M,self.rect.center)


class PromptButton(Button):
	'''
	used for yes/no/ok options throughout the game
	'''
	def __init__(self,groups,pos,text):
		super().__init__(groups)
		self.set_image('graphics/ui/buttons/prompt',True)
		self.rect = self.image.get_rect(topleft=pos)
		self.create_text(text,WHITE,TEXT_M,self.rect.center)