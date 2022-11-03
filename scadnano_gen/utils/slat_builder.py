from ast import literal_eval as make_tuple
from lxml import etree as ET
from typing import Union

from utils.slats import CrissCrossSlat, CrissCrossStaple

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
