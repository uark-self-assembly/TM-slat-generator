from ast import literal_eval as make_tuple
from lxml import etree as ET
from typing import Union

import scadnano as sc
from utils.sequence_mapper import SequenceMapper

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
	sequence_mapper: SequenceMapper,
	domain_length: int = 5,
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
				domain_length,
				sequence_mapper
			)
		# Vertical slat
		elif slat.orientation == 'N':
			AddVerticalSlat(
					slat,
					design,
					num_helices - y - 1,
					x,
					domain_length,
					sequence_mapper
				)
		# Horizontal slat
		else:
			AddHorizontalSlat(
				slat,
				design,
				num_helices - y - 1,
				x,
				domain_length,
				sequence_mapper
			)

def AddFrontierTooth(
	design: sc.Design,
	start_helix: int,
	offset: int,
	height: int,
	domain_length: int,
	sequence_mapper: SequenceMapper,
) -> None:
	""" Add a frontier tooth/staple to the design.

	Add a frontier tooth/staple to :param design:, the bottom of which starts at
	:param start_helix:. :param offset: determines the leftmost offset the frontier
	tooth occupies. :param height: determines how many rows it will occupy.

	Will not check if this is a valid placement, so it can trigger a scadnano.StrandError if
	used incorrectly!

	TODO: Sequences are not assigned to these. Add this unless you want them to fly away
	from the assembly at breakneck speeds.
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
	slat: CrissCrossSlat,
	design: sc.Design,
	helix: int,
	x_position: int,
	domain_length: int,
	sequence_mapper: SequenceMapper,
) -> None:
	""" Add a horizontal slat to the design.

	Add a horizontal slat to ``design`` at ``helix`` and offset equal to ``x_position`` * ``domain_length``.
	``slat`` is the object describing exactly what kind of slat is at the given position.

	Will assign DNA sequence if ``domain_to_sequence`` is provided.

	Will not check if this is a valid placement, so it can trigger a scadnano.StrandError if
	used incorrectly!

	TODO: Explain parameters.
	"""

	# Generate list of domains from slat object and position parameters
	offset = x_position * domain_length
	domains = [
		BuildDomain(
			helix,
			offset + (i * domain_length),
			bool(helix % 2),
			domain_length,
			AdjustSequence(
				sequence_mapper.getSequenceByDomain(domain_label),
				InsertionNeeded(offset + (i * domain_length), domain_length),
			)
		)

		for i, domain_label in enumerate(slat)
	]

	# If even row, flip order of domains to match direction of strand propagation
	if helix % 2 == 0:
		domains.reverse()

	# Add strand to design
	design.add_strand(sc.Strand(domains))

def AddVerticalSlat(
slat: CrissCrossSlat,
design: sc.Design,
start_helix: int,
x_position: int,
domain_length: int,
sequence_mapper: SequenceMapper,
) -> None:
	""" Add a vertical slat to the design.

	Add a vertical slat to :param design:, the bottom of which begins at :param start_helix:
	(y direction) and :param offset: (x direction). :param length: determines how many rows
	this slat will span.

	Will not check if this is a valid placement, so it can trigger a scadnano.StrandError if
	used incorrectly!

	TODO: Parameters have changed, update documentation.
	"""

	offset = x_position * domain_length
	insertion_needed = InsertionNeeded(offset, domain_length)
	domains = [
		BuildDomain(
			start_helix - helix,
			offset,
			not bool((start_helix - helix) % 2),
			domain_length,
			AdjustSequence(sequence_mapper.getSequenceByDomain(domain_label), insertion_needed)
		)

		for helix, domain_label in enumerate(slat)
	]

	design.add_strand(sc.Strand(domains))

def BuildDomain(
	helix: int,
	offset: int,
	forward: bool,
	domain_length: int,
	dna_sequence: Union[str, None]
) -> sc.Domain:
	"""Builds a scadnano domain complete with potential insertions and provided base pair sequence.

	TODO
	"""
	
	return sc.Domain(
		helix=helix,
		forward=forward,
		start=offset,
		end=offset + domain_length,
		insertions=GetInsertions(offset, domain_length),
		dna_sequence=dna_sequence
	)

def GetInsertions(offset: int, domain_length: int) -> list[tuple[int, int]]:
	"""TODO: Document
	
	TODO
	"""
	
	if InsertionNeeded(offset, domain_length):
		return [(offset + (domain_length // 2), 1),]
	else:
		return list()

def AdjustSequence(
	sequence: str,
	insertion_present: bool,
) -> Union[str, None]:
	"""Adds a base pair in the middle of the domain if it needs to account for an insertion.
	"""
	# This is an artifact of bad planning on my part, so there's certainly a cleaner way to
	# go about this that I just don't have time for.
	if insertion_present:
		half_index = len(sequence) // 2
		sequence = sequence[:half_index] + 'T' + sequence[half_index:]

	return sequence

def InsertionNeeded(offset: int, domain_length: int) -> bool:
	"""TODO
	
	TODO: There is probably a better alternative for this.
	"""

	# TODO: Hardcoded value here; should be dependent on domain length
	return (offset // domain_length) % 4 == 0