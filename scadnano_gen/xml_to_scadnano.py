from getopt import getopt
import sys
from utils.sequence_mapper import SequenceMapper

from utils.design_builder import BuildScadnanoDesign
from utils.slat_builder import GetPolyominoTypes

def main():

	# Get command-line parameters
	options = GetOptions()
	input_file_name, domain_length, ox_dna_flag = GetParams(options)
	input_file_path = f'./assemblies/{input_file_name}'

	# Get slat types from XML file
	slats = GetPolyominoTypes(input_file_path)

	# TODO: Potentially utilize user input
	sequence_mapper = SequenceMapper()

	# Create scadnano design from assembly
	design = BuildScadnanoDesign(slats, input_file_path, domain_length, sequence_mapper)

	# Write to .sc file with the same name as the .xml assembly
	assembly_name = input_file_name.split('.xml')[0]
	output_file = f'{assembly_name}.sc'
	design.write_scadnano_file('./sc_designs/', output_file)
	
	# Produce OxDNA files for assembly
	if ox_dna_flag:
		# TODO: Change output names to assembly name
		#		Pretty sure the API isn't working correctly in that regard...
		design.write_oxdna_files('./oxdna_files/')

def GetParams(options: list[tuple[str, str]]) -> tuple[str, int, bool]:
	"""
	Get parameters supplied by user in command line.

	Returns <input assembly file>, <domain length>, and <oxdna output flag>.
	"""

	# Default values
	input_file = None
	domain_length = 5
	oxdna_output = False

	for option, param in options:

		if option in ['-h', '--help']:
			DisplayHelp()
		elif option in ['-i', '--input']:
			input_file = param
		elif option in ['-d', '--domain']:
			try:
				domain_length = int(param)
			except:
				DisplayHelp()
		elif option in ['-o', '--oxdna']:
			oxdna_output = True

		# TODO: Option to provide domain-to-sequence mapping

	if input_file is None:
		# Display help and terminate program
		DisplayHelp()

	return input_file, domain_length, oxdna_output

def GetOptions() -> list[tuple[str, str]]:

	try:
		options, _ = getopt(
			sys.argv[1:],
			'hi:d:o',
			['help', 'input=', 'domain=', 'oxdna',]
		)
	except:
		print(f'\nUnrecognized option: {sys.argv[1:]}')
		DisplayHelp()

	return options

def DisplayHelp():
	"""
	Displays help for running the script. Terminates the program.
	"""

	print('-h, --help\t\t\t\tDisplays this help message.')
	print('-i <file.xml>, --input=<file.xml>\t[Required] Input assembly file.')
	print('-d <int>, --domain=<int>\t\t[Optional] Domain length (default=5).')
	print('-o, --oxdna\t\t\t\tOutput OxDNA files of assembly.')

	exit()

# Driver code
if __name__ == '__main__':

	main()
