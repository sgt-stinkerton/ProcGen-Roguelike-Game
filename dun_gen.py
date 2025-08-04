import pygame
import random
from copy import deepcopy

from perlin_noise import PerlinNoise
from settings import *

class Node:
	'''
	node within tree, holds own data and data of children
	'''
	def __init__(self,data,left=None,right=None):
		self.data = data
		self.left = left
		self.right = right


class BSPTree:
	'''
	tree of rects created to represent dungeon map
	'''
	def __init__(self,tree=None):
		self.tree = tree
		self.leaf_node_rects = []
		self.MIN_NODE_SIZE = 16 # smallest split that can be made
		self.create_tree()

	def create_tree(self):
		# creates main rect which entire tree (dungeon) is within
		map_rect = pygame.Rect((0,0),(MAP_WIDTH,MAP_HEIGHT))
		self.tree = self.split_tree(map_rect)

	def split_tree(self,rect):
		# splits nodes of tree
		node = Node(data=rect)
		if rect.width > self.MIN_NODE_SIZE*2 or rect.height > self.MIN_NODE_SIZE*2:
			# splits are made until the size of the nodes are too small to split
			left_child, right_child = self.split_direction(rect)
			node.left = self.split_tree(left_child)
			node.right = self.split_tree(right_child)
		else:
			# if split cannot be made, current node is added to a list of leaf nodes
			self.leaf_node_rects.append(rect)
		return node

	def split_direction(self,rect):
		# decides which direction to split the current node

		# ratio unbalanced in one direction: split to balance
		if (rect.width/rect.height > 1.5):
			rect_a, rect_b = self.split_vertical(rect)
		elif (rect.height/rect.width > 1.5):
			rect_a, rect_b = self.split_horizontal(rect)
		else:

			# ratio relatively balanced, and both lengths are large enough to split: 
			# choosing random direction to split
			if rect.width > self.MIN_NODE_SIZE*2 and rect.height > self.MIN_NODE_SIZE*2:
				if random.randint(0,1):
					rect_a, rect_b = self.split_horizontal(rect)
				else:
					rect_a, rect_b = self.split_vertical(rect)

			# ratio relatively balanced, but only one side is large enough to split:
			elif rect.height > self.MIN_NODE_SIZE*2:
				rect_a, rect_b = self.split_horizontal(rect)
			else:
				rect_a, rect_b = self.split_vertical(rect)

		return rect_a, rect_b

	def split_horizontal(self,rect):
		# node's height is split
		rect_a = pygame.Rect.copy(rect)
		rect_b = pygame.Rect.copy(rect)

		rect_a.height -= random.randint(self.MIN_NODE_SIZE,
										rect_a.height - self.MIN_NODE_SIZE)
		rect_b.height -= rect_a.height
		rect_b.y += rect_a.height

		return rect_a, rect_b

	def split_vertical(self,rect):
		# node's width is split
		rect_a = pygame.Rect.copy(rect)
		rect_b = pygame.Rect.copy(rect)

		rect_a.width -= random.randint(self.MIN_NODE_SIZE,
									   rect_a.width - self.MIN_NODE_SIZE)
		rect_b.width -= rect_a.width
		rect_b.x += rect_a.width

		return rect_a, rect_b


class Tilemap:
	'''
	creates 2D array (tilemap) of dungeon based on tree data created by BSPTree
	to be used when blitting tiles to screen
	'''
	def __init__(self,map_tree,leaf_nodes):
		self.map_tree = map_tree		# holds rect data of every node
		self.leaf_nodes = leaf_nodes 	# holds rect data of nodes which will have rooms
		self.tilemap = [] 				# 2D array for tile values
		self.rooms = []					# list holding rect data of every room
		self.smallest_room = None 		# smallest room in the dungeon assigned as the player spawn

		# room generation constants
		self.MIN_ROOM_SIZE = 7
		self.MAX_ROOM_SIZE = 16
		self.PADDING = 4  				# ensures rooms do not touch

		# walker algorithm values
		self.WEIGHTING = 0.2
		self.north = 1.0
		self.east = 1.0
		self.south = 1.0
		self.west = 1.0

		self.draw_tilemap()

	def create_empty_tilemap(self):
		# all tiles initially set to wall tiles
		self.tilemap = [['0' for x in range(MAP_WIDTH)]
						for y in range(MAP_HEIGHT)]
		return self.tilemap

	def draw_tilemap(self):
		# draws out entire tilemap, initially using leaf node list

		self.tilemap = self.create_empty_tilemap()
		for leaf in self.leaf_nodes:
			room = self.draw_room(leaf)

			# draws out floor tiles onto array where there are rooms
			for y in range(room.y, room.y + room.height):
				for x in range(room.x, room.x + room.width):
					self.tilemap[y][x] = '.'

		self.draw_corridors(self.map_tree)
		self.erode()
		self.rooms.remove(self.smallest_room) # so mobs cannot be placed into spawn room

	def draw_room(self, rect):
		# draws room of current leaf onto tilemap grid, using rect data of the leaf

		room = pygame.Rect.copy(rect)

		# random width
		room.width = random.randint(self.MIN_ROOM_SIZE, 
			min(room.width - (self.PADDING*2), self.MAX_ROOM_SIZE))
			# the max size cannot be bigger than the max room size, but also accounts
			# for the padding - takes smaller of the two as the max

		# random x coordinate positioning
		if room.width < rect.width / 2:
			room.x = random.randint(
				rect.centerx - room.width + 1, rect.centerx - 1)
		else:
			room.x += random.randint(0, rect.right -
									 room.right - (self.PADDING*2))
			room.x += self.PADDING

		# random height
		room.height = random.randint(self.MIN_ROOM_SIZE, min(
			room.height - (self.PADDING*2), self.MAX_ROOM_SIZE))
		
		# random y coordinate positioning
		if room.height < rect.height / 2:
			room.y = random.randint(
				rect.centery - room.height + 1, rect.centery - 1)
		else:
			room.y += random.randint(0, rect.bottom -
									 room.bottom - (self.PADDING*2))
			room.y += self.PADDING

		self.find_smallest(room) # checks if current room is the smallest so far
		self.rooms.append(room)
		return room

	def find_smallest(self,room):
		# smallest room becomes the player spawn room in the dungeon
		if self.smallest_room is None:
			self.smallest_room = room
		else:
			# checks size of smallest room by calculating area
			if room.width*room.height < self.smallest_room.width*self.smallest_room.height:
				self.smallest_room = room

	def draw_corridors(self,tree):
		if tree.left is None:
			# cannot draw corridors between non-existent nodes
			# tree will always have either 0 or 2 children, only need to check for 1
			return	

		# joins nodes via centers: all rooms are at least half of the 
		# width/height of the node, so they will always be joined
		a_center = tree.left.data.center
		b_center = tree.right.data.center

		# connects x coords
		horizontal_corr = pygame.Rect(min(a_center[0], b_center[0]), b_center[1], 	# x, y
									 abs(a_center[0] - b_center[0])+1, 2) 			# width, height
		# connects y coords
		vertical_corr = pygame.Rect(a_center[0], min(a_center[1], b_center[1]), 	# x, y
									2, abs(a_center[1] - b_center[1]))				# width, height

		corridors = [horizontal_corr, vertical_corr]

		# draws corridors out on tilemap
		for corridor in corridors:
			for y in range(corridor.y, corridor.y + corridor.height):
				for x in range(corridor.x, corridor.x + corridor.width):
					if self.tilemap[y][x] == '0':  # doesn't overwrite room tiles
						self.tilemap[y][x] = 'c'

		# draws corridors between children nodes until no longer possible
		self.draw_corridors(tree.left)
		self.draw_corridors(tree.right)

	def erode(self):
		# deteriorates rooms and corridors, making them look less uniform

		for walker in range(MAP_WIDTH*(MAP_HEIGHT//2)):
			self.reset_weighting() # resets any prior walker weighting

			# chooses random coordinate position for walker to begin at
			rand_y = random.randrange(1, MAP_HEIGHT)
			rand_x = random.randrange(1, MAP_WIDTH)

			if self.tile_check(rand_y,rand_x):
				walker_life = random.randint(1,3)
				hit_empty_tile = True # hit a tile which can be eroded

				while walker_life > 0 and hit_empty_tile is True:

					walker_life -= 1 # decrement walker life span; only makes certain amount of steps
					move_y, move_x = self.walker_dir(rand_y,rand_x)

					# checking that next move is not out of bounds
					while (move_y <= 0) or (move_x <= 0) or (
						move_y >= MAP_HEIGHT - 1) or (move_x >= MAP_WIDTH - 1):
						move_y, move_x = self.walker_dir(rand_y,rand_x)

					# checking if walker has hit an empty tile
					if self.tilemap[move_y][move_x] != '0':
						hit_empty_tile = False
					else:
						self.tilemap[move_y][move_x] = '.'

					rand_y, rand_x = move_y, move_x

	def tile_check(self, rand_y, rand_x):
		# if surroundings tiles can be eroded, weight walker in their direction

		if self.tilemap[rand_y][rand_x] != '0':

			if self.tilemap[rand_y - 1][rand_x] == '0':
				self.north += self.WEIGHTING

			if self.tilemap[rand_y][rand_x + 1] == '0':
				self.east += self.WEIGHTING

			if self.tilemap[rand_y + 1][rand_x] == '0':
				self.south += self.WEIGHTING

			if self.tilemap[rand_y][rand_x - 1] == '0':
				self.west += self.WEIGHTING

			return True
		else:
			return False

	def walker_dir(self, rand_y, rand_x):
		# choosing a direction to move based on weighted values

		# normalising the weighted values
		total = self.north+self.east+self.south+self.west
		self.north /= total
		self.east /= total
		self.south /= total
		self.west /= total

		random_val = random.random()
		if 0 <= random_val < self.north:
			# move north
			move_y = rand_y - 1
			move_x = rand_x
		elif self.north <= random_val < self.north+self.east:
			# move east
			move_y = rand_y
			move_x = rand_x + 1
		elif self.north+self.east <= random_val < self.north+self.east+self.south:
			# move south
			move_y = rand_y + 1
			move_x = rand_x
		else:
			# move west
			move_y = rand_y
			move_x = rand_x - 1

		return move_y, move_x

	def reset_weighting(self):
		# resets weighting so new walker not influenced by previous movement
		self.north, self.east, self.south, self.west = 1.0, 1.0, 1.0, 1.0


class DungeonMap:
	'''
	takes tilemap produced by TileMap class and changes the values of each 'tile'
	(item in the list) to ones which correspond with 
	'''
	def __init__(self, tilemap):
		# unpacking tilemap parameter
		self.tilemap = tilemap.tilemap
		self.map_tree = tilemap.map_tree
		self.leaf_nodes = tilemap.leaf_nodes
		self.rooms = tilemap.rooms
		self.start_room = tilemap.smallest_room
		self.player_spawn = self.start_room.center

		# change floor terrain
		self.place_dirt()

		# if deepcopy not used, then changes to new list are reflected on old list 
		self.tilemap_copy = deepcopy(self.tilemap)		# used as reference when setting tile values
		self.tilemap_overlay = deepcopy(self.tilemap)	# used to place non-floor/wall tiles
		
		# give wall and dirt tiles values
		for tile in ['0','D']:
			self.set_tile_vals(tile)

		# other dungeon generation
		self.exit_room = self.set_exit()
		self.place_flowers()
		self.place_mobs()

	def generate_perlin(self, octaves):
		# generates perlin noise image (2D list) of values resembling static
		noise = PerlinNoise(octaves=octaves, seed=random.randint(0,100000))
		x, y = MAP_WIDTH, MAP_HEIGHT
		overlay = [[noise([i/x, j/y]) for j in range(x)] for i in range(y)]
		return overlay

	def place_dirt(self):
		# creates variation in floor tiles by adding patches of dirt
		overlay = self.generate_perlin(octaves=8)
		for y, row in enumerate(overlay):
			for x, col in enumerate(row):
				if col >= 0.09 and self.tilemap[y][x] == '.':
					self.tilemap[y][x] = 'D'

	def set_tile_vals(self,tile):
		# gives each tile a value, calculated by checking surrounding tiles

		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
				if self.tilemap_copy[y][x] == tile:
					# looks at each of the 8 surrounding tiles around any given tile

					n = self.tile_check(x, y-1, tile)
					s = self.tile_check(x, y+1, tile)
					w = self.tile_check(x-1, y, tile)
					e = self.tile_check(x+1, y, tile)

					nw = (self.tile_check(x-1, y-1, tile) and n and w)
					ne = (self.tile_check(x+1, y-1, tile) and n and e)
					sw = (self.tile_check(x-1, y+1, tile) and s and w)
					se = (self.tile_check(x+1, y+1, tile) and s and e)

					# calculates value for that combination of 3x3 tile grid
					tile_value = nw + n*2 + ne*4 + w*8 + e*16 + sw*32 + s*64 + se*128

					# DungeonState needs to know if the tile is dirt or regular floor
					if tile == 'D':
						tile_value = 'D' + str(tile_value)

					self.tilemap[y][x] = tile_value

	def tile_check(self, x, y, check):
		# checks if tile == target tile

		# try/except catches border (list index out of range) errors
		try:	
			if self.tilemap_copy[y][x] == check:
				# if checked tile = target
				return True
			return False
		except:
			# tiles next to out of range items should appear as edges
			return True

	def set_exit(self):
		# sets the room in which the exit to the dungeon is found
		self.exit_room = random.choice(self.rooms)
		self.tilemap_overlay[self.exit_room.centery][self.exit_room.centerx] = 'X'
		return self.exit_room

	def place_mobs(self):
		# places mobs onto tilemap overlay
		for room in self.rooms:
			# each room must have at least one enemy
			x = random.randint(room.x+1, room.x+room.width - 1)
			y = random.randint(room.y+1, room.y+room.height - 1)
			self.tilemap_overlay[y][x] = 'M'
			for i in range(2):
				# additional random enemy spawning
				if (random.randint(1,3)) >= 2:
					x = random.randint(room.x+1, room.x+room.width - 1)
					y = random.randint(room.y+1, room.y+room.height - 1)
					self.tilemap_overlay[y][x] = 'M'

	def place_flowers(self):
		# places (breakable) flowers onto tilemap overlay
		overlay = self.generate_perlin(octaves=20)
		for y, row in enumerate(overlay):
			for x, col in enumerate(row):
				if col >= 0.21 and self.tilemap_overlay[y][x] != '0':
					self.tilemap_overlay[y][x] = 'F'


def get_dungeon():
	# generates actual dungeon
	dungeon_tree = BSPTree()
	tilemap = Tilemap(dungeon_tree.tree, dungeon_tree.leaf_node_rects)
	dungeon_map = DungeonMap(tilemap)
	return dungeon_map