from ast import literal_eval as make_tuple
import warnings
from lxml import etree as ET
import scadnano as sc
import sys
from typing import Union
from utils.slats import CrissCrossSlat, CrissCrossStaple

# System constants
# TODO: Take user input
EIGHT_DOMAIN_OFFSET = 40
TWELVE_DOMAIN_OFFSET = int(EIGHT_DOMAIN_OFFSET * 1.5)
FOUR_DOMAIN_OFFSET = EIGHT_DOMAIN_OFFSET // 2

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
	xml_tree = ET.parse(filename, None)
	polyomino_types = xml_tree.getroot()[1]

	for poly_type in polyomino_types:
		
		# Note: If a name is duplicated, this will overwrite a polyomino with another
		slat = BuildSlat(poly_type)
		name_to_slat[slat.name] = slat

	return name_to_slat

"""
Can't set type of param: polyomino_type because ElementTree is unclear.
param: polyomino type is an XML element whose children can be accessed via index.

TODO: Document!
"""
def BuildSlat(polyomino_type) -> Union[CrissCrossSlat, CrissCrossStaple]:
	
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
			# Four y-values (5 through 8); decrement y coordinate due to how staples are stored
			for y in range(8, 4, -1):
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
	xml_polyominoes = ET.parse(input_file, None).getroot()[3][0]
	# num_helices, max_offset = GetSystemBounds(slats, xml_polyominoes)
	
	# TODO: Create "helices"
		# How many? Need to read assembly to find out...

	# TODO: Place slats one-by-one

	# TODO: Insertions

"""
Returns the number of helices and max offset needed for the scadnano system.
"""
def GetSystemBounds(
	slats: dict[str, Union[CrissCrossSlat, CrissCrossStaple]],
	xml_polyominoes
) -> tuple[int, int]:

	num_helices: int = 0	# Number of "rows" in scadnano system
	max_offset: int = 0		# Maximum distance on the x-axis in scadnano system
	
	for polyomino in xml_polyominoes:
		
		# The what (polyomino type) and the where (translation)
		name: str = polyomino[0].text
		translation: tuple[int, int, int] = make_tuple(polyomino[1].text)

		slat = slats[name]
		# Vertical slat or frontier tooth/staple
		if (slat.orientation == 'N'):
			# if (num_helices)	TODO: Left off here
			pass
		# Horizontal slat
		else:
			pass

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
	BuildScadnanoSystem(slats, input_file)
