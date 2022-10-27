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
		slat = BuildSlatType(poly_type)
		name_to_slat[slat.name] = slat

	return name_to_slat

"""
TODO: Document!
TODO: Set polyomino_type type and handle None data.
"""
def BuildSlatType(polyomino_type) -> Union[CrissCrossSlat, CrissCrossStaple]:
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

def LocateSlat(
	polyomino: ET._Element,
	slats: dict[str, Union[CrissCrossSlat, CrissCrossStaple]]
) -> Union[
	tuple[Union[CrissCrossSlat, CrissCrossStaple], int, int, int],
	None
]:
	"""
	:param polyomino: XML element containing slat name (type) and location in assembly.
	Returns (Polyomino (slat/staple), x, y, z) or None if information is missing in XML element.
	"""
	name = polyomino[0].text
	str_translation = polyomino[1].text

	if name is None or str_translation is None:
		return
	
	translation: tuple[int, int, int] = make_tuple(str_translation)

	return slats[name], translation[0], translation[1], translation[2]

"""
TODO: Handle polyominoes that can rotate or have negative coords in structure definition.
"""
def GetSystemBounds(
	xml_polyominoes: ET._Element,
	slats: dict[str, Union[CrissCrossSlat, CrissCrossStaple]]
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

	return min_row, max_row + 1, min_column * DOMAIN_LENGTH, (max_column + 1) * DOMAIN_LENGTH

"""
TODO: Document!
"""
def AddStrands(design: sc.Design, xml_polyominoes: ET._Element, num_helices: int) -> None:

	for polyomino in xml_polyominoes:

		# Get slat type and location in the assembly
		slat_data = LocateSlat(polyomino, slats)
		if slat_data is None:
			continue
		slat = slat_data[0]
		x = slat_data[1]
		y = slat_data[2]
		z = slat_data[3]

		# (Odd row and z=0 slat) OR (even row and z=-1 slat)
		if (y % 2) ^ bool(z):
			# 5' to 3' goes left
			# TODO
			pass
		# (Even row and z=0 slat) OR (odd row and z=-1 slat)
		else:
			# 5' to 3' goes right
			# TODO: Frontier teeth currently only span one column at bottom
			num_columns = len(slat) if z else 1
			design.draw_strand(num_helices - y - 1, x * DOMAIN_LENGTH)\
				.move(num_columns * DOMAIN_LENGTH)

"""
TODO: Document!
"""
def BuildScadnanoDesign(
	slats: dict[str, Union[CrissCrossSlat, CrissCrossStaple]],
	input_file: str
) -> sc.Design:

	# Access to <Polyominoes> (the child of <assembly>, which is a child of <PolyominoSystem>)
	xml_polyominoes = ET.parse(input_file).getroot()[3][0]

	# Get necessary parameters for creating the scadnano system
	min_row, max_row, min_offset, max_offset = GetSystemBounds(xml_polyominoes, slats)
	num_helices = max_row - min_row

	# Instantiate blank design
	helices = [sc.Helix(max_offset, min_offset) for _ in range(num_helices)]
	design = sc.Design(helices=helices, grid=sc.square)
	
	AddStrands(design, xml_polyominoes, num_helices)

	# TODO: Add insertions

	return design

if __name__ == '__main__':

	# TODO: Receive input regarding domain length
	if len(sys.argv) != 2:
		print('Please provide exactly one argument: filename.xml!')
		exit()

	# Name of .xml assembly file
	input_file = sys.argv[1]

	# Get slat types from XML file
	slats = GetPolyominoTypes(input_file)

	# Create scadnano design from assembly and save to file
	design = BuildScadnanoDesign(slats, input_file)
	design.write_scadnano_file()
