from typing import Union
from utils.slats import CrissCrossSlat, CrissCrossStaple, MacroTile

def GetSeedRowColor(seed_num: int, max_num: int) -> str:

	if seed_num == 0:
		return 'PINK'
	elif seed_num == 1:
		return 'BLUE'
	elif seed_num == max_num:
		return 'RED'
	else:
		return 'GREEN'

def GetTileColor(symbol: str) -> str:

	if symbol == 'HEAD':
		return 'RED'
	elif symbol == '0':
		return 'WHITE'
	elif symbol == '1':
		return 'YELLOW'
	elif symbol == 'BLANK':
		return 'BLUE'
	elif symbol == 'EDGE':
		return 'PINK'
	else:
		return 'BLACK'

def BuildOutputGlues(
	slat_row: int,
	input_prefix: str,
	output_prefix: str,
	a_cells: list[str],
	b_cells: list[str],
	left_out: bool = True,
	low_to_high: bool = False,
) -> list[str]:
	"""
	Returns 8 glues for a slat that connects a tile to the right to its
	same-row neighbor to the left.
	"""
	offset = CrissCrossSlat.BINDING_THRESH
	if low_to_high:
		offset *= (-1)

	# Connect same-row neighbor to the left
	if left_out:

		glue1_even = output_prefix + a_cells[slat_row + offset]
		glue1_odd = output_prefix + b_cells[slat_row + offset]
		glue2_even = input_prefix + a_cells[slat_row]
		glue2_odd = input_prefix + b_cells[slat_row]

		output_glues = [
			glue1_even,
			glue1_odd,
			glue1_even,
			glue1_odd,
			glue2_even,
			glue2_odd,
			glue2_even,
			glue2_odd,
		]

		return output_glues
	# Connect same-row neighbor to the right
	else:
		glue1_even = input_prefix + a_cells[slat_row]
		glue1_odd = input_prefix + b_cells[slat_row]
		glue2_even = output_prefix + a_cells[slat_row + offset]
		glue2_odd = output_prefix + b_cells[slat_row + offset]

		output_glues = [
			glue1_even,
			glue1_odd,
			glue1_even,
			glue1_odd,
			glue2_even,
			glue2_odd,
			glue2_even,
			glue2_odd,
		]

		return output_glues

def ExtendOutputSlat(
	input_slat: Union[CrissCrossSlat, list[str]],
	slat_row: int,
	output_prefix: str,
	a_cells: list[str],
	b_cells: list[str],
	seed_row: bool = False,
	extend_west: bool = False,
) -> None:
	"""
	Adds four output glues to the end of parameter 'input_slat'. These glues
	carry information to the next simulated row (i.e., upwards).
	"""
	offset = 0
	if seed_row:
		offset = CrissCrossSlat.BINDING_THRESH

	even_glue = output_prefix + a_cells[slat_row + offset]
	odd_glue = output_prefix + b_cells[slat_row + offset]
	extension = [even_glue, odd_glue, even_glue, odd_glue]

	if extend_west and type(input_slat) is list:
		input_slat = extension + input_slat
	elif extend_west and type(input_slat) is CrissCrossSlat:
		input_slat.SetGlues(extension + input_slat.glues)
	else:
		input_slat += extension

def BuildTileSlats(
	tile: MacroTile,
	a_cells: list[str],
	b_cells: list[str],
	build_output: bool = False,
	force_double_out: bool = False,
) -> list[CrissCrossSlat]:
	"""
	Receive macro-tile input/output information and build the necessary
	macro-tile and output slats.
	"""
	slats = []
	letters = ['a', 'b', 'c', 'd',]
	slat_length = CrissCrossSlat.STD_SLAT_LEN
	binding_thresh = CrissCrossSlat.BINDING_THRESH

	a_name = tile.name + '_a'
	b_name = tile.name + '_b'
	a_glues, b_glues = [], []
	
	quarter_len = binding_thresh >> 1	# Divide by 2

	if tile.even_row:

		for i in range(slat_length):

			if tile[i]:
				if i < binding_thresh:
					a_glues.append(tile.name + f'_{a_cells[i]}')
					b_glues.append(tile.name + f'_{b_cells[i]}')
				else:
					a_glues.append(f'{tile[i]}_{a_cells[i]}')
					b_glues.append(f'{tile[i]}_{b_cells[i]}')
			else:
				a_glues.append(None)
				b_glues.append(None)

		slats.append(CrissCrossSlat(a_name, 'N', a_glues, tile.color))
		slats.append(CrissCrossSlat(b_name, 'N', b_glues, tile.color))

		if build_output:

			for i in range(binding_thresh):

				left_out = not (force_double_out or i < quarter_len)
				output_glues = BuildOutputGlues(
					i,
					tile.name + '_',
					tile[i] + '_',
					a_cells,
					b_cells,
					left_out=left_out
				)
				slats.append(CrissCrossSlat(f'{tile.name}_{letters[i]}_out', 'E', output_glues))

	else:
		for i in range(slat_length):

			if tile[i]:
				if (i < quarter_len) or (i >= slat_length - quarter_len):
					a_glues.append(tile.name + f'_{a_cells[i]}')
					b_glues.append(tile.name + f'_{b_cells[i]}')
				else:
					a_glues.append(f'{tile[i]}_{a_cells[i]}')
					b_glues.append(f'{tile[i]}_{b_cells[i]}')
			else:
				a_glues.append(None)
				b_glues.append(None)

		slats.append(CrissCrossSlat(a_name, 'N', a_glues, tile.color))
		slats.append(CrissCrossSlat(b_name, 'N', b_glues, tile.color))

		if build_output:
			
			for i in range(binding_thresh):

				row = i
				if i >= quarter_len:
					row += binding_thresh

				if tile[row]:
					output_glues = BuildOutputGlues(
						row,
						tile.name + '_',
						tile[row] + '_',
						a_cells,
						b_cells,
						left_out=False,
						low_to_high=(True if row >= binding_thresh else False),
					)
					slats.append(CrissCrossSlat(f'{tile.name}_{letters[i]}_out', 'E', output_glues))

	return slats

def BuildStaple(
	name: str,
	in_glue: str,
	out_glue: str,
	a_cells: list[str],
	b_cells: list[str],
	build_output: bool = False
) -> list[Union[CrissCrossStaple, CrissCrossSlat]]:

	a_letters = ['A', 'B', 'C', 'D']
	b_letters = ['W', 'X', 'Y', 'Z']
	west_glues = []
	east_glues = []

	for i in range(CrissCrossStaple.BINDING_THRESH):

		if i < CrissCrossStaple.BINDING_THRESH // 2:
			west_glues.append(f'{name}_{a_letters[i]}')
			east_glues.append(f'{name}_{b_letters[i]}')
		else:
			west_glues.append(f'{in_glue}_{a_letters[i]}')
			east_glues.append(f'{in_glue}_{b_letters[i]}')

	components = [CrissCrossStaple(name, west_glues + east_glues),]

	if build_output:

		a_glues = BuildOutputGlues(0, f'{name}_', f'{out_glue}_', a_cells, b_cells, False)
		b_glues = BuildOutputGlues(1, f'{name}_', f'{out_glue}_', a_cells, b_cells, False)
		a_out_slat = CrissCrossSlat(f'{name}_a_out', 'E', a_glues)
		b_out_slat = CrissCrossSlat(f'{name}_b_out', 'E', b_glues)

		components += [a_out_slat, b_out_slat]

	return components