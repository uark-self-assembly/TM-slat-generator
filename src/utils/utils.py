from lxml import etree as et
from typing import Union
from utils.slats import CrissCrossSlat, CrissCrossStaple

def GetTMDefinition(input_file: str) -> tuple:

	with open(input_file, 'r') as file:

		tape_alphabet = []
		blank_symbol = ''
		states = []
		start_state = ''
		transitions = []

		p = 0
		lines = file.readlines()

		for line in lines:

			if len(line) > 0:

				if line.strip() == 'Alphabet:':
					p = 0
				elif line.strip() == 'States:':
					p = 1
				elif line.strip() == 'Start State:':
					p = 2
				elif line.strip() == 'Transitions:':
					p = 3
				elif line.strip() == 'Blank Symbol:':
					p = 4
				else:
					if p == 0:
						tape_alphabet = line.strip().split(',')
					elif p == 1:
						states = line.strip().split(',')
					elif p == 2:
						start_state = line.strip()
					elif p == 4:
						blank_symbol = line.strip()
					else:
						trans_list = line.strip().split(',')
						transitions.append(tuple(trans_list))

		return tape_alphabet, blank_symbol, states, start_state, transitions

def TilesetToXML(
	tileset: list[Union[CrissCrossSlat, CrissCrossStaple]],
	output_file: str
) -> None:

	sys_elem = et.Element('PolyominoSystem')
	et.SubElement(sys_elem, 'rotation').text = 'False'
	et.SubElement(sys_elem, 'min_binding').text = '1'
	et.SubElement(sys_elem, 'bindingThreshold').text = '4'
	
	types_elem = et.SubElement(sys_elem, 'PolyominoTypes')
	seed_elem = et.SubElement(sys_elem, 'seed')
	et.SubElement(sys_elem, 'assembly')

	for slat in tileset:
		poly_type = et.SubElement(types_elem, 'PolyominoType')
		et.SubElement(poly_type, 'name').text = slat.name
		et.SubElement(poly_type, 'color').text = slat.color
		et.SubElement(poly_type, 'concentration').text = '1.0'
		blocks = et.SubElement(poly_type, 'blocks')
		
		if(slat.orientation == 'N'):

			for y in range(len(slat)):

				block = et.SubElement(blocks, 'block')

				x = 0

				# If polyomino is a frontier tooth/staple and we have already iterated over the left half
				if type(slat) is CrissCrossStaple and y >= len(slat) // 2:
					x = 1
					y -= len(slat) // 2

				et.SubElement(block, 'coords').text = f'({x}, {y}, 0)'

				domain_index = len(slat) - y - 1
				if slat[domain_index]:
					domains = et.SubElement(block, 'domains')
					domain = et.SubElement(domains, 'domain')
					et.SubElement(domain, 'label').text = slat[domain_index]
					et.SubElement(domain, 'direction').text = 'D'
					et.SubElement(domain, 'strength').text = '1'

		else:
			for x in range(len(slat)):
				block = et.SubElement(blocks, 'block')
				et.SubElement(block, 'coords').text = f'({x}, 0, 0)'

				glue = slat[x]
				if glue:	# Unnecessary for our purposes, but does keep things nice and general
					domains = et.SubElement(block, 'domains')
					domain = et.SubElement(domains, 'domain')
					et.SubElement(domain, 'label').text = glue + '*'
					et.SubElement(domain, 'direction').text = 'U'
					et.SubElement(domain, 'strength').text = '1'

	seed_tiles = et.SubElement(seed_elem, 'Polyominoes')

	for i in range(2):
		slat_a = et.SubElement(seed_tiles, 'Polyomino')
		et.SubElement(slat_a, 'PolyominoType').text = 'seed0_a'
		et.SubElement(slat_a, 'translation').text = f'({i * 2}, 0, 0)'

		slat_b = et.SubElement(seed_tiles, 'Polyomino')
		et.SubElement(slat_b, 'PolyominoType').text = 'seed0_b'
		et.SubElement(slat_b, 'translation').text = f'({(i * 2) + 1}, 0, 0)'

	et.ElementTree(sys_elem).write(output_file, pretty_print=True)