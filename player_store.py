import os
from json import load, dump
from copy import deepcopy

class TempStore:
	'''
	class that, when initialised, gets passed between every state by the game loop
	in order to transfer user data between states, as well as save data externally
	to be imported in another session
	'''
	def __init__(self):
		self.base_data = { # base player stats - used when new game is created
		'health': 20,
		'attack': 15,   
		'mana_amt': 50,
		'mana': 0.05,
		'stamina': 40,
		'speed': 3.5,
		'wisps': 0,
		'dungeons': 0}
		self.data = {} # current player data
		self.save_data = {} # imported save data from chosen save file
		self.save_slot = None # slot number of save which data has been loaded from

	def get_current(self):
		# retrieves current player data
		if not self.data:
			# if it doesn't exist, use the base stats as player data
			self.data = self.base_data.copy()
		return self.data

	def update_current(self, updated):
		# updates current player data
		self.data = updated

	def import_save(self, slot):
		# imports data from selected save
		with open('saves/save'+slot+'.txt') as save_file:
			self.save_data = load(save_file)
		self.data = deepcopy(self.save_data)
		self.save_slot = slot

	def create_new_save(self, slot):
		# creates new save file using base data 
		# (when new game is created) 
		with open('saves/save'+slot+'.txt','w') as save_file:
			dump(self.base_data,save_file)
		self.save_data = deepcopy(self.base_data)
		self.save_slot = slot

	def write_to_save(self):
		# updates currently in-use save file with current player data
		with open('saves/save'+self.save_slot+'.txt','w') as save_file:
			dump(self.data,save_file)
		self.save_data = deepcopy(self.data)

	def check_for_saves(self):
		# checks for existence of save files in saves directory
		
		if not os.path.exists('saves'):
			os.makedirs('saves')
		
		if not os.listdir('saves'):
			return False
		else:
			return True

	def count_used_slots(self):
		# returns number of save files in saves directory
		used_slots = 0
		for file in os.listdir('saves'):
			if file.endswith('.txt'):
				used_slots += 1
		return used_slots

	def delete_save(self, slots_used):
		# deletes selected save file
		os.remove('saves/save'+self.save_slot+'.txt')
		if slots_used > 1:
			if self.save_slot == '1':
				# if there is more than 1 save file and the 1st save is being deleted,
				# rename 2nd save to be the 1st (to appear correctly in the load saves menu)
				os.rename('saves/save2.txt', 'saves/save1.txt')
			if slots_used == 3 and self.save_slot != '3':
				# if 3 slots are in use and the user has deleted the 1st or 2nd save,
				# rename the 3rd save to be the 2nd
				os.rename('saves/save3.txt', 'saves/save2.txt')