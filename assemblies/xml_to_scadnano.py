from ast import literal_eval as make_tuple
import warnings
from lxml import etree as ET
import scadnano as sc
import sys
from typing import Union
from utils.slats import CrissCrossSlat, CrissCrossStaple

# System constants
# TODO: Take user input
DOMAIN_LENGTH = 5

"""
sys_elem (PolyominoSystem) has 4 children:
	[0] bindingThreshold
	[1] PolyominoTypes
	[2] seed
	[3] assembly

TODO: Document!
"""
def GetPolyominoTypes(filename: str) -> dict[str, Union[CrissCrossSlat, CrissCrossStaple]]:

	name_to_slat: dict[str, Union[CrissCrossSlat, CrissCrossStaple]] = dict()
	xml_tree = ET.parse(filename)
	polyomino_types = xml_tree.getroot()[1]

	for poly_type in polyomino_types:
		
		# Note: If a name is duplicated, this will overwrite a polyomino with another
		slat = BuildSlat(poly_type)
		name_to_slat[slat.name] = slat

	return name_to_slat

"""
TODO: Document!
TODO: Set polyomino_type type and handle None data.
"""
def BuildSlat(polyomino_type) -> Union[CrissCrossSlat, CrissCrossStaple]:
	"""
	:param polyomino_type: An XML element whose children can be accessed via index.
	"""
	
	# Name of the polyomino type
	name: str = polyomino_type[0].text

	# Element containing all glues and their relative positions
	blocks = polyomino_type[3]

	# Maps coordinates to domain
	coord_to_domain = dict()
	for block in blocks:

		# Get coordinates
		coords = make_tuple(block[0].text)

		# TODO: Print warning if multiple domains per coordinate are detected
		# domains_elem = block[1]
		# if len(domains_elem) > 1:
		# 	warnings.warn(
		# 		f'Multiple domains detected for {name} at {coords}!',
		# 		Warning
		# 	)

		# Coordinates with no domain will be caught here and stored as None
		try:
			domain = block[1][0][0].text
		except IndexError:
			domain = None

		coord_to_domain[coords[:2]] = domain

	# Check if this is a staple/"frontier tooth"
	if (0, 1) in coord_to_domain and (1, 1) in coord_to_domain:	# TODO: Changed here and below elif
		
		domains = list()

		# Two x-values (a left and a right side)
		for x in range(2):
			# TODO: Hard-coded values here are yucky
			# Four y-values (3 through 0); decrement y coordinate due to how staples are stored
			for y in range(3, -1, -1):
				domains.append(coord_to_domain[(x, y)])

		return CrissCrossStaple(name, domains)

	# Check if this is a vertical slat
	elif (0, 1) in coord_to_domain:
		# Iterate through y component
		domains = [coord_to_domain[(0, y)] for y in range(len(coord_to_domain))]

		return CrissCrossSlat(name, 'N', domains)

	# This is a horizontal slat
	else:
		# Iterate through x component
		domains = [coord_to_domain[(x, 0)] for x in range(len(coord_to_domain))]

		return CrissCrossSlat(name, 'E', domains)

"""
TODO: Document!
"""
def BuildScadnanoSystem(
	slats: dict[str, Union[CrissCrossSlat, CrissCrossStaple]],
	input_file: str
) -> sc.Design:

	# Access to <Polyominoes> (the child of <assembly>, which is a child of <PolyominoSystem>)
	xml_polyominoes = ET.parse(input_file).getroot()[3][0]

	# Get necessary parameters for creating the scadnano system
	min_row, max_row, min_offset, max_offset = GetSystemBounds(slats, xml_polyominoes)
	
	# TODO: Create "helices"
		# How many? Need to read assembly to find out...

	# TODO: Place slats one-by-one

	# TODO: Insertions

"""
TODO: Handle polyominoes that can rotate or have negative coords in structure definition.
"""
def GetSystemBounds(
	slats: dict[str, Union[CrissCrossSlat, CrissCrossStaple]],
	xml_polyominoes: ET._Element
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
		
		if (polyomino[0].text is None or polyomino[1].text is None):
			continue
		
		# Get slat type and location in assembly
		name: str = polyomino[0].text
		translation: tuple[int, int, int] = make_tuple(polyomino[1].text)
		x = translation[0]
		y = translation[1]
		slat = slats[name]

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

	return min_row, max_row, min_column * DOMAIN_LENGTH, (max_column + 1) * DOMAIN_LENGTH

if __name__ == '__main__':

	# TODO: Receive input regarding domain length
	if len(sys.argv) != 2:
		print('Please provide exactly one argument: filename.xml!')
		exit()

	# Name of .xml assembly file
	input_file = sys.argv[1]

	# Get slat types from XML file
	slats = GetPolyominoTypes(input_file)

	# Create scadnano file from assembly
	# system = BuildScadnanoSystem(slats, input_file)

	# TODO: Write system to file
