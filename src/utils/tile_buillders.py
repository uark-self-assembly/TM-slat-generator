from typing import Union

import utils.builder_helpers as help
from utils.slats import CrissCrossSlat, CrissCrossStaple, MacroTile

def GetInputTiles(
	assembly_input: str,
	start_state: str,
	blank: str,
	a_cells: list[str],
	b_cells: list[str],
) -> list[CrissCrossSlat]:

	slats = []
	assembly_input = assembly_input[::-1]	# Reverse the input string (tiles are generated in reverse)
	letters = ['a', 'b', 'c', 'd',]		# Gross duplicate data TO-DO
	slat_length = CrissCrossSlat.STD_SLAT_LEN
	binding_thresh = CrissCrossSlat.BINDING_THRESH

	# Per iteration:
	#	- Creates 2 slats for each simulated macro-tile from right bound to leftmost input cell
	#	- Creates 4 slats for input/output between tiles
	for i in range(len(assembly_input) + 2):	# +2 for two right-hand boundary tiles
		# === Macro-tile slats === #
		prefix = 'seed' + str(i)
		a_name = prefix + '_a'
		a_glues = []

		if i == 0:
			for j in range(binding_thresh):
				glue = prefix + a_cells[j]
				a_glues.append(glue)
		else:
			for j in range(slat_length):
				glue = prefix + a_cells[j]
				a_glues.append(glue)

		# Quick and dirty change to seed row colors (tiles now colored according to input symbol)
		max_index = len(assembly_input) + 1		# len(assembly_input) + 2 - 1
		if i < 2 or i == max_index:
			color = help.GetSeedRowColor(i, max_index)
		else:
			color = help.GetTileColor(assembly_input[i - 2])

		a_slat = CrissCrossSlat(a_name, 'N', a_glues, color)
		slats.append(a_slat)

		b_name = prefix + '_b'
		b_glues = []

		if i == 0:
			for j in range(binding_thresh):
				glue = prefix + b_cells[j]
				b_glues.append(glue)
		else:
			for j in range(slat_length):
				glue = prefix + b_cells[j]
				b_glues.append(glue)

		b_slat = CrissCrossSlat(b_name, 'N', b_glues, color)
		slats.append(b_slat)

		# === Output connector slats === #
		next_prefix = 'seed' + str(i + 1)

		for j in range(binding_thresh):
			output_glues = help.BuildOutputGlues(j, prefix, next_prefix, a_cells, b_cells)

			# b & d output slats; need to carry tape info to next row up (physically to the right).
			output_prefix = None
			if j < 2:
				# Border tile
				if i == 0:
					output_prefix = 'E-o_EDGE_'
				# Edge blank tile
				elif i == 1:
					output_prefix = f'E-o_{blank}+_'
				# Input tape cells
				elif i < len(assembly_input) + 1:
					output_prefix = assembly_input[i - 2] + '_'	# -2 because of two edge tape cells
				# Tile with TM head
				else:
					output_prefix = f'{start_state},{assembly_input[i - 2]}_'
				
				help.ExtendOutputSlat(output_glues, j, output_prefix, a_cells, b_cells, True)

			output_slat = CrissCrossSlat(prefix + '_' + letters[j] + '_out', 'E', output_glues)
			slats.append(output_slat)

	# === Seed-row west growth blank === #
	#	- 2 more tile slats
	#	- 4 more output slats
	# Dev note: It is made separately from above because of poor planning
	# on this programmer's behalf.
	prefix = f'seed{len(assembly_input) + 2}'
	a_name = prefix + '_a'
	b_name = prefix + '_b'
	a_glues, b_glues = [], []

	for i in range(slat_length):
		a_glues.append(prefix + a_cells[i])
		b_glues.append(prefix + b_cells[i])

	slats.append(CrissCrossSlat(a_name, 'N', a_glues, 'BLUE'))
	slats.append(CrissCrossSlat(b_name, 'N', b_glues, 'BLUE'))

	for i in range(binding_thresh):
		name = prefix + f'_{letters[i]}_out'
		# b & d slats
		if i < 2:
			output_glues = help.BuildOutputGlues(i, prefix, 'W-e_EDGE_', a_cells, b_cells)
			help.ExtendOutputSlat(output_glues, i, f'W-o_{blank}+_', a_cells, b_cells, True)
			slats.append(CrissCrossSlat(name, 'E', output_glues))
		# a & c slats
		else:
			output_glues = help.BuildOutputGlues(i, prefix, '<_', a_cells, b_cells)
			slats.append(CrissCrossSlat(name, 'E', output_glues))

	return slats

def GetBoundaryTiles(
	blank: str,
	a_cells: list[str],
	b_cells: list[str]
) -> list[Union[CrissCrossSlat, CrissCrossStaple]]:
	
	slats = []

	# == Even West Edge == #
	tile = MacroTile('W-e_EDGE', help.GetTileColor('EDGE'), True)
	tile.SetGlues('W-o_EDGE', 'W-o_EDGE', 'W-e_EDGE', '<')
	temp_slats = help.BuildTileSlats(tile, a_cells, b_cells, True, True)
	# Extra long (12-length) slats at indices 4 & 5
	help.ExtendOutputSlat(temp_slats[4], 2, '>_', a_cells, b_cells)
	help.ExtendOutputSlat(temp_slats[5], 3, '>_', a_cells, b_cells)
	slats += temp_slats

	# == Odd West Edge == #
	tile = MacroTile('W-o_EDGE', help.GetTileColor('EDGE'), False)
	tile.SetGlues(None, 'W-e_EDGE', 'W-o_EDGE', '<')
	slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

	# == Even East Edge == #
	tile = MacroTile('E-e_EDGE', help.GetTileColor('EDGE'), True)
	tile.SetGlues('<', 'E-o_EDGE', 'E-e_EDGE', 'E-e_EDGE')
	slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

	# == Odd East Edge == #
	tile = MacroTile('E-o_EDGE', help.GetTileColor('EDGE'), False)
	tile.SetGlues('>', 'E-e_EDGE', 'E-o_EDGE', None)
	slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

	# == Even West BLANK+ Copy == #
	tile = MacroTile(f'W-e_{blank}+', help.GetTileColor('BLANK'), True)
	tile.SetGlues('<', f'W-o_{blank}+', f'W-e_{blank}+', '<')
	slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

	# == Even East BLANK+ Copy == #
	tile = MacroTile(f'E-e_{blank}+', help.GetTileColor('BLANK'), True)
	tile.SetGlues('<', f'E-o_{blank}+', f'E-e_{blank}+', '<')
	slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

	# == Odd West BLANK+ Copy == #
	tile = MacroTile(f'W-o_{blank}+', help.GetTileColor('BLANK'), False)
	tile.SetGlues('>', f'W-e_{blank}+', f'W-o_{blank}+', '>')
	slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

	# == Odd East BLANK+ Copy == #
	tile = MacroTile(f'E-o_{blank}+', help.GetTileColor('BLANK'), False)
	tile.SetGlues('>', f'E-e_{blank}+', f'E-o_{blank}+', '>')
	temp_slats = help.BuildTileSlats(tile, a_cells, b_cells, True)
	# Extend output slats for edge's double-strength glue
	help.ExtendOutputSlat(temp_slats[4], 6, 'E-e_EDGE_', a_cells, b_cells)
	help.ExtendOutputSlat(temp_slats[5], 7, 'E-e_EDGE_', a_cells, b_cells)
	slats += temp_slats

	slats += GetGrowthTiles(blank, a_cells, b_cells)

	return slats

def GetGrowthTiles(
	blank: str,
	a_cells: list[str],
	b_cells: list[str],
) -> list[Union[CrissCrossSlat, CrissCrossStaple]]:

	slats = []

	# == East (odd) growth edge == #
	tile = MacroTile(f'E_EDGE_GROW', help.GetTileColor('EDGE'), False)
	tile.SetGlues(
		f'E_GROW',
		f'E-e_{blank}+',
		'E-o_EDGE',
		'E-in_STAPLE'
	)
	temp_slats = help.BuildTileSlats(tile, a_cells, b_cells, True)
	# Extend south-eastern output slats to length 12
	help.ExtendOutputSlat(temp_slats[4], 6, 'E-e_EDGE_', a_cells, b_cells)
	help.ExtendOutputSlat(temp_slats[5], 7, 'E-e_EDGE_', a_cells, b_cells)
	slats += temp_slats

	# == East growth staples == #
	slats += help.BuildStaple('E_STAPLE', 'E-in_STAPLE', 'E-e_EDGE', a_cells, b_cells, True)

	# == West (even) growth edge == #
	tile = MacroTile('W_EDGE_GROW', help.GetTileColor('EDGE'), True)
	tile.SetGlues(
		f'W_{blank}+_GROW',
		f'W_{blank}+_GROW',
		'W-e_EDGE',
		'W_GROW'
	)
	temp_slats = help.BuildTileSlats(tile, a_cells, b_cells, True, True)
	help.ExtendOutputSlat(temp_slats[4], 2, '>_', a_cells, b_cells)
	help.ExtendOutputSlat(temp_slats[5], 3, '>_', a_cells, b_cells)
	slats += temp_slats

	# == West growth blanks (tile slats) == #
	# Sit on odd rows, but tile-body slat glues behave like even tiles
	tile = MacroTile(f'W_{blank}+_GROW', help.GetTileColor(blank), True)
	tile.SetGlues(
		'W-o_EDGE',
		f'W-e_{blank}+',
		f'W_{blank}+_GROW',
		f'W_{blank}+_GROW'
	)
	temp_slats = help.BuildTileSlats(tile, a_cells, b_cells, True)
	# Extend output slats (on western side) to length 12
	help.ExtendOutputSlat(temp_slats[2], 4, 'W-o_EDGE_', a_cells, b_cells, extend_west=True)
	help.ExtendOutputSlat(temp_slats[3], 5, 'W-o_EDGE_', a_cells, b_cells, extend_west=True)
	slats += temp_slats

	return slats

def GetSymbolCopyTiles(
	tape_alphabet: list,
	a_cells: list[str],
	b_cells: list[str],
) -> list[CrissCrossSlat]:

	slats = []

	for symbol in tape_alphabet:

		# Even row
		tile = MacroTile(f'e_{symbol}', help.GetTileColor(symbol), True)
		tile.SetGlues('<', symbol, symbol, '<')
		slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

		# Odd row
		tile = MacroTile(f'o_{symbol}', help.GetTileColor(symbol), False)
		tile.SetGlues('>', symbol, symbol, '>')
		slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

	return slats

def GetTransitionTiles(
	transitions: list,
	blank: str,
	a_cells: list[str],
	b_cells: list[str]
) -> list[CrissCrossSlat]:

	slats = []

	for transition in transitions:

		start_state = transition[0]
		start_symbol = transition[1]
		end_state = transition[2]
		end_symbol = transition[3]
		direction = transition[4]

		if direction == 'R':
			# == (1) Odd row (fast) == #
			tile = MacroTile(f'o_{start_state},{start_symbol}', help.GetTileColor('HEAD'), False)
			tile.SetGlues(start_state, end_symbol, start_symbol, end_state)
			slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

			# == (2) Odd row at eastern boundary == #
			if start_symbol == blank:

				tile = MacroTile(
					f'o-grow_{start_state},{start_symbol}',
					help.GetTileColor('HEAD'),
					False
				)
				tile.SetGlues(
					start_state,
					f'{start_state},{start_symbol}',
					f'E-o_{start_symbol}+',
					'E_GROW'
				)
				slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

			# == (3) Odd row signal pickup == #
			tile = MacroTile(
				f'o-trans_{start_state},{start_symbol}',
				help.GetTileColor(end_symbol),
				False
			)
			tile.SetGlues('>', end_symbol, f'{start_state},{start_symbol}', end_state)
			slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

			# == (4) Even row == #
			# Generic
			tile = MacroTile(
				f'e_{start_state},{start_symbol}',
				help.GetTileColor('HEAD'),
				True
			)
			tile.SetGlues(
				'<',
				f'{start_state},{start_symbol}',
				start_symbol,
				start_state
			)
			slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

			# Boundary blank
			if start_symbol == blank:
				tile = MacroTile(
					f'e_{start_state},{start_symbol}+',
					help.GetTileColor('HEAD'),
					True
				)
				tile.SetGlues(
					'<',
					f'{start_state},{start_symbol}',
					f'W-e_{start_symbol}+',
					start_state
				)
				slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

			# == (5) Even row no-op == #
			tile = MacroTile(
				f'e-No-Op_{start_state},{start_symbol}',
				help.GetTileColor('HEAD'),
				True
			)
			tile.SetGlues(
				'<',
				f'{start_state},{start_symbol}',
				f'{start_state},{start_symbol}',
				'<'
			)
			slats += help.BuildTileSlats(tile, a_cells, b_cells, True)
		
		else:
			# == (1) Even row (fast) == #
			tile = MacroTile(f'e_{start_state},{start_symbol}', help.GetTileColor('HEAD'), True)
			tile.SetGlues(end_state, end_symbol, start_symbol, start_state)
			slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

			# == (2) Even row at western boundary == #
			if start_symbol == blank:

				tile = MacroTile(
					f'e-grow_{start_state},{start_symbol}',
					help.GetTileColor('HEAD'),
					True
				)
				tile.SetGlues(
					'W_GROW',
					f'{start_state},{start_symbol}',
					f'W-e_{start_symbol}+',
					start_state
				)
				slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

			# == (3) Even row signal pickup == #
			tile = MacroTile(
				f'e-trans_{start_state},{start_symbol}',
				help.GetTileColor(end_symbol),
				True
			)
			tile.SetGlues(
				end_state,
				end_symbol,
				f'{start_state},{start_symbol}',
				'<'
			)
			slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

			# == (4) Odd row == #
			# Generic
			tile = MacroTile(
				f'o_{start_state},{start_symbol}',
				help.GetTileColor('HEAD'),
				False
			)
			tile.SetGlues(
				f'{start_state}',
				f'{start_state},{start_symbol}',
				start_symbol,
				'>'
			)
			slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

			# Boundary blank
			if start_symbol == blank:
				tile = MacroTile(
					f'o_{start_state},{start_symbol}+',
					help.GetTileColor('HEAD'),
					False
				)
				tile.SetGlues(
					start_state,
					f'{start_state},{start_symbol}',
					f'E-o_{start_symbol}+',
					'>'
				)
				temp_slats = help.BuildTileSlats(tile, a_cells, b_cells, True)
				help.ExtendOutputSlat(temp_slats[4], 6, 'E-e_EDGE_', a_cells, b_cells)
				help.ExtendOutputSlat(temp_slats[5], 7, 'E-e_EDGE_', a_cells, b_cells)
				slats += temp_slats

			# == (5) Odd row no-op == #
			tile = MacroTile(
				f'o-No-Op_{start_state},{start_symbol}',
				help.GetTileColor('HEAD'),
				False
			)
			tile.SetGlues(
				'>',
				f'{start_state},{start_symbol}',
				f'{start_state},{start_symbol}',
				'>'
			)
			slats += help.BuildTileSlats(tile, a_cells, b_cells, True)

	return slats
