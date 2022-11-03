import sys

from utils.design_builder import BuildScadnanoDesign
from utils.slat_builder import GetPolyominoTypes

def main():

	# TODO: Receive input regarding domain length
	if len(sys.argv) != 2:
		print('Please provide exactly one argument: filename.xml!')
		exit()

	# Path to .xml assembly file (produced by PolyominoTAS)
	input_file = f'./assemblies/{sys.argv[1]}'

	# TODO: Take user input instead (leave this as default value)
	domain_length = 5

	# Get slat types from XML file
	slats = GetPolyominoTypes(input_file)

	# Create scadnano design from assembly
	design = BuildScadnanoDesign(slats, input_file, domain_length)

	# Write to .sc file with the same name as the .xml assembly
	assembly_name = sys.argv[1].split('.xml')[0]
	output_file = f'{assembly_name}.sc'
	design.write_scadnano_file('./sc_designs/', output_file)

# Driver code
if __name__ == '__main__':

	main()
