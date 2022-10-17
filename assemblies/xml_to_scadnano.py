from ast import literal_eval as make_tuple
import warnings
from lxml import etree as ET
import sys
from typing import Union
from utils.slats import CrissCrossSlat, CrissCrossStaple

# TODO
# Notes: z=0 (vertical) slats start one coordinate northward to their translation
#		 z=-1 (horizontal) slats actually make sense

"""
TODO: Document

sys_elem (PolyominoSystem) has 4 children:
	[0] bindingThreshold
	[1] PolyominoTypes
	[2] seed
	[3] assembly
"""
def GetPolyominoTypes(filename: str) -> list[Union[CrissCrossSlat, CrissCrossStaple]]:

	slats: list[Union[CrissCrossSlat, CrissCrossStaple]] = []
	xml_tree = ET.parse(filename, None)
	polyomino_types = xml_tree.getroot()[1]

	for poly_type in polyomino_types:
		
		slats.append(BuildSlat(poly_type))

	return slats

"""
TODO: Document
Can't set type of param: polyomino_type because ElementTree is unclear.
param: polyomino type is an XML element whose children can be accessed via index.
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

	# Stores the domains of this slat in order
	# domains = list()

	# Check if this is a staple/"frontier tooth"
	if (0, 8) in coord_to_domain and (1, 8) in coord_to_domain:
		pass

	# Check if this is a vertical slat
	elif (0, 8) in coord_to_domain:
		# Vertical slat coordinates start at 1 and go to 8
		domains = [coord_to_domain[(0, y)] for y in range(1, len(coord_to_domain) + 1)]

		return CrissCrossSlat(name, 'N', domains)

	# This is a horizontal slat
	else:
		# Horizontal slat coordinates behave nicely (start at zero, end at len - 1)
		domains = [coord_to_domain[(x, 0)] for x in range(len(coord_to_domain))]

		return CrissCrossSlat(name, 'E', domains)

if __name__ == '__main__':

	if len(sys.argv) != 2:
		print('Please provide exactly one argument: filename.xml!')
		exit()

	slats = GetPolyominoTypes(sys.argv[1])
