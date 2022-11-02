import sys

from utils.design_builder import BuildScadnanoDesign
from utils.slat_builder import GetPolyominoTypes

def main():

	# TODO: Receive input regarding domain length
	if len(sys.argv) != 2:
		print('Please provide exactly one argument: filename.xml!')
		exit()

	# Name of .xml assembly file
	input_file = sys.argv[1]

	# TODO: Take user input instead (leave this as default value)
	domain_length = 5

	# Get slat types from XML file
	slats = GetPolyominoTypes(input_file)

	# Create scadnano design from assembly and save to file
	design = BuildScadnanoDesign(slats, input_file, domain_length)
	design.write_scadnano_file()

# Driver code
if __name__ == '__main__':

	main()
