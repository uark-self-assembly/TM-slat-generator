from getopt import getopt
import sys
from time import time

import utils.tile_buillders as build
from utils.utils import GetTMDefinition, TilesetToXML

def DisplayHelp():

	print('-h, --help\t\t\t\tDisplays this help message.')
	print('-i <input>, --input=<input>\t\tSeed string as input.')
	print('-f <filename>, --file=<filename>\t[Optional] Text file containing a description of a Turing machine.')
	print('-o <filename>, --output=<filename>\t[Optional] Name of xml file to output the tileset to.')
	print('-v, --verbose\t\t\t\tRun in verbose mode.')

	exit()

if __name__ == '__main__':

	try:
		options, extraparams = getopt(
			sys.argv[1:],
			'hi:f:o:v',
			['help', 'input=' 'file=', 'output=', 'verbose',]
		)
	except:
		print('\nUnrecognized option: ' + str(sys.argv[1:]))

	input_file = 'turing-machine.txt'
	output_file = 'TM-tileset.xml'
	assembly_input = None
	verbose = False

	for o, p in options:

		if o in ['-h', '--help']:
			DisplayHelp()
		elif o in ['-i', '--input']:
			assembly_input = p
		elif o in ['-f', '--file']:
			input_file = p
		elif o in ['-o', '--ouptut']:
			output_file = p
		elif o in ['-v', '--verbose']:
			verbose = True
		else:
			DisplayHelp()

	if assembly_input is None:
		print('\nNo input string specified!')
		DisplayHelp()
	
	tape_alphabet, blank_symbol, states, start_state, transitions = GetTMDefinition('../turing_machines/' + input_file)
	a_cells = ['A', 'B', 'C', 'D', 'a', 'b', 'c', 'd',]
	b_cells = ['W', 'X', 'Y', 'Z', 'w', 'x', 'y', 'z',]

	if verbose:
		print('\nGenerating tileset...\t', end='')
		start = time()
	
	input_slats = build.GetInputTiles(assembly_input, start_state, blank_symbol, a_cells, b_cells)
	bound_slats = build.GetBoundaryTiles(blank_symbol, a_cells, b_cells)
	symbol_slats = build.GetSymbolCopyTiles(tape_alphabet, a_cells, b_cells)
	transition_slats = build.GetTransitionTiles(transitions, blank_symbol, a_cells, b_cells)
	tile_set = input_slats + bound_slats + symbol_slats + transition_slats

	if verbose:
		end = time()
		print(f'{(end - start):.3f}')
		print('Saving XML document...\t', end='')
		start = time()

	TilesetToXML(tile_set, '../slats/' + output_file)

	if verbose:
		end = time()
		print(f'{(end - start):.3f}')

	print(f'\nTransition slats:\t{len(transition_slats)}')
	print(f'Boundary slats:\t\t{len(bound_slats)}')
	print(f'Symbol slats:\t\t{len(symbol_slats)}')
	print(f'Seed row slats:\t\t{len(input_slats)}')
	print(f'Origami adapters:\t\t{len(assembly_input) + 5}')
	print('============================')
	print(f'Singly seeded total:\t{len(tile_set)}')
	print(f'Origami total:\t\t{len(tile_set) - len(input_slats) + len(assembly_input) + 5}')

	if verbose:
		print('\nCounting unique domains... ', end='')
		start = time()
		input_domains = {}
		domains = {}

		# This is an estimation in order to account for the fact that a
		# DNA origami will be used for the input row...
		for slat in input_slats:
			for domain in slat:
				if domain in input_domains:
					input_domains[domain] += 1
				else:
					input_domains[domain] = 1

		domain_offset = len(input_domains) - (8 * 4)	# Approx. domains shared by other sets of slats

		for slat in tile_set:
			for domain in slat:
				if domain in domains:
					domains[domain] += 1
				else:
					domains[domain] = 1

		end = time()
		print(f'{(end - start):.3f}\nUnique domains:\t{len(domains) - domain_offset}')

	print('\n===== DONE =====')
