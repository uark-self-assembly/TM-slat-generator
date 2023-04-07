from lxml import etree as ET
from typing import Union

import scadnano as sc
from utils.sequence_mapper import SequenceMapper

from utils.slats import CrissCrossSlat, CrissCrossStaple
from utils.strand_builders import AddStrands, LocateSlat

"""
TODO: Document!
"""
def BuildScadnanoDesign(
	slats: dict[str, Union[CrissCrossSlat, CrissCrossStaple]],
	input_file: str,
	domain_length: int,
	sequence_mapper: SequenceMapper,
) -> sc.Design:

	# Access to <Polyominoes> (the child of <assembly>, which is a child of <PolyominoSystem>)
	xml_polyominoes = ET.parse(input_file).getroot()[3][0]

	# Get necessary parameters for creating the scadnano system
	min_row, max_row, min_offset, max_offset =\
		GetSystemBounds(xml_polyominoes, slats, domain_length)
	num_helices = max_row - min_row

	# Instantiate blank design
	helices = [sc.Helix(max_offset, min_offset) for _ in range(num_helices)]
	design = sc.Design(helices=helices, grid=sc.square)
	
	# Add strands
	AddStrands(
		design,
		xml_polyominoes,
		slats,
		num_helices,
		sequence_mapper,
		domain_length,
	)

	return design

"""
TODO: Handle polyominoes that can rotate or have negative coords in structure definition.
"""
def GetSystemBounds(
	xml_polyominoes: ET._Element,
	slats: dict[str, Union[CrissCrossSlat, CrissCrossStaple]],
	domain_length: int
) -> tuple[int, int, int, int]:
	"""
	:param slats: A dictionary mapping string names to slat types.
	:param xml_polyominoes: XML element <Polyominoes>, the sole child of <assembly>.

	Returns (min_row, max_row, min_offset, max_offset).
	"""
	
	min_row: int = 0	# Smallest row index (according to abstract assembly)
	max_row: int = 0	# Largest row index (according to abstract assembly)
	min_column: int = 0	# Smallest "column" index (according to abstract assembly)
	max_column: int = 0	# Largest "column" index (according to abstract assembly)
	
	# Iterate over all polyominoes in the saved assembly
	for polyomino in xml_polyominoes:

		# Get slat type and location in the assembly
		slat_data = LocateSlat(polyomino, slats)
		if slat_data is None:
			continue
		slat = slat_data[0]
		x = slat_data[1]
		y = slat_data[2]

		# == Frontier tooth/staple == #
		if slat is CrissCrossStaple:
			# Update number of helices (design's vertical dimension)
			end_row = y + (len(slat) // 2) - 1
			if end_row > max_row:
				max_row = end_row
			# Not mutually exclusive conditions
			if y < min_row:
				min_row = y

			# Update length of helices (design's horizontal dimension)
			end_column = x + 1
			if end_column > max_column:
				max_column = end_column
			# Mutually exclusive conditions
			elif x < min_column:
				min_column = x

		# == Vertical slat == #
		elif slat.orientation == 'N':
			# Update number of helices (design's vertical dimension)
			end_row = y + len(slat) - 1
			if end_row > max_row:
				max_row = end_row
			# Not mutually exclusive conditions
			if y < min_row:
				min_row = y

			# Update length of helices (design's horizontal dimension)
			if x > max_column:
				max_column = x
			# Mutually exclusive conditions
			elif x < min_column:
				min_column = x

		# == Horizontal slat == #
		else:
			# Update number of helices (design's vertical dimension)
			if y > max_row:
				max_row = y
			# Mutually exclusive conditions
			elif y < min_row:
				min_row = y

			# Update length of helices (design's horizontal dimension)
			end_column = x + len(slat) - 1
			if end_column > max_column:
				max_column = end_column
			# Not mutually exclusive conditions
			if x < min_column:
				min_column = x

	return min_row, max_row + 1, min_column * domain_length, (max_column + 1) * domain_length
