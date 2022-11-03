from ast import literal_eval as make_tuple
from lxml import etree as ET
from typing import Union

import scadnano as sc

from utils.slats import CrissCrossSlat, CrissCrossStaple

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
TODO: Document!
"""
def AddStrands(
	design: sc.Design,
	xml_polyominoes: ET._Element,
	slats: dict[str, Union[CrissCrossSlat, CrissCrossStaple]],
	num_helices: int,
	domain_length: int = 5
) -> None:

	for polyomino in xml_polyominoes:

		# Get slat type and location in the assembly
		slat_data = LocateSlat(polyomino, slats)
		if slat_data is None:
			continue

		slat, x, y, _ = slat_data

		# Frontier tooth
		if type(slat) is CrissCrossStaple:
			AddFrontierTooth(
				design,
				num_helices - y - 1,
				x * domain_length,
				len(slat) // 2,
				domain_length
			)
		# Vertical slat
		elif slat.orientation == 'N':
			AddVerticalSlat(
				design,
				num_helices - y - 1,
				x * domain_length,
				len(slat),
				domain_length
			)
		# Horizontal slat
		else:
			AddHorizontalSlat(
				design,
				num_helices - y - 1,
				x * domain_length,
				len(slat),
				domain_length
			)

def AddFrontierTooth(
	design: sc.Design,
	start_helix: int,
	offset: int,
	height: int,
	domain_length: int
) -> None:
	""" Add a frontier tooth/staple to the design.

	Add a frontier tooth/staple to :param design:, the bottom of which starts at
	:param start_helix:. :param offset: determines the leftmost offset the frontier
	tooth occupies. :param height: determines how many rows it will occupy.

	Will not check if this is a valid placement, so it can trigger a scadnano.StrandError if
	used incorrectly!
	"""

	tooth_width = domain_length * 2

	for helix in range(start_helix, start_helix - height, -1):

		# Odd row
		if helix % 2:
			start_offset = offset + tooth_width
			width_vector = tooth_width * (-1)

		# Even row
		else:
			start_offset = offset
			width_vector = tooth_width

		# Add strand to design
		design.draw_strand(helix, start_offset).move(width_vector)

		# Determines crossover behavior for arbitrary sized staples
		full_crossover = not ((helix - start_helix) % 2)

		# Uppermost row: Add nick
		if helix == start_helix - height + 1:
			design.add_nick(helix, offset + domain_length, helix % 2 == 0)

		# Row is above the start row: Add full crossover
		if helix < start_helix and full_crossover:
			design.add_full_crossover(helix, helix + 1, offset + domain_length, width_vector > 0)

		# Row is above the start row: Add one half crossover on each edge
		elif helix < start_helix:
			design.add_half_crossover(helix, helix + 1, offset, width_vector > 0)
			design.add_half_crossover(helix, helix + 1, offset + tooth_width - 1, width_vector > 0)

def AddHorizontalSlat(
	design: sc.Design,
	helix: int,
	offset: int,
	length: int,
	domain_length: int
) -> None:
	""" Add a horizontal slat to the design.

	Add a horizontal slat to :param design: at :param helix: with leftmost offset of
	:param offset:. :param length: determines how far (in the x direction) the strand
	should span.

	Will not check if this is a valid placement, so it can trigger a scadnano.StrandError if
	used incorrectly!
	"""

	width_vector = length * domain_length
	
	if helix % 2 == 0:
		offset += width_vector
		width_vector *= -1

	design.draw_strand(helix, offset).move(width_vector)

def AddVerticalSlat(
	design: sc.Design,
	start_helix: int,
	offset: int,
	length: int,
	domain_length: int
) -> None:
	""" Add a vertical slat to the design.

	Add a vertical slat to :param design:, the bottom of which begins at :param start_helix:
	(y direction) and :param offset: (x direction). :param length: determines how many rows
	this slat will span.

	Will not check if this is a valid placement, so it can trigger a scadnano.StrandError if
	used incorrectly!
	"""

	for helix in range(start_helix, start_helix - length, -1):

		start_offset = offset			# Offset of the 5' end of strand
		crossover_offset = offset		# Offset at which to add the crossover
		width_vector = domain_length	# Either positive or negative domain length
		
		# Odd helix: Vertical strands go backward (left)
		if helix % 2:
			start_offset += domain_length
			width_vector *= -1
			# Modify crossover positions depending on strand offset (x position)
			if (offset / domain_length) % 2:
				crossover_offset += domain_length - 1

		# Even helix: Modify crossover positions depending on strand offset (x position)
		elif (offset / domain_length) % 2 == 0:
			crossover_offset += domain_length - 1
		
		# Add strand to design
		design.draw_strand(helix, start_offset).move(width_vector)

		# Add crossovers to create one continuous strand
		if helix < start_helix:
			design.add_half_crossover(helix, helix + 1, crossover_offset, helix % 2 == 0)

