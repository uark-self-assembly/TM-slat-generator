from io import TextIOWrapper

class Transition():

	tape_alphabet = None
	states = None
	
	def __init__(self) -> None:

		self.start_state = None
		self.start_symbol = None
		self.end_state = None
		self.end_symbol = None
		self.direction = None

	def SetClassVars(alphabet: list[str], states: list[str]) -> None:

		Transition.tape_alphabet = alphabet
		Transition.states = states

	def GetInput(self, var: str) -> str:

		user_input = input(f'{var}: ')
		while user_input == '':
			user_input = input(f'{var}: ')

		return user_input

	def GetDirection(self) -> str:

		direction = input('Direction: ')
		while direction != 'R' and direction != 'L':
			direction = input('Direction: ')

		return direction

	def GetUserTransition(self) -> None:
		
		self.start_state = self.GetInput('Start State')
		while self.start_state not in Transition.states:
			self.start_state = self.GetInput('Start State')

		self.start_symbol = self.GetInput('Start Symbol')
		while self.start_symbol not in Transition.tape_alphabet:
			self.start_symbol = self.GetInput('Start Symbol')

		self.end_state = self.GetInput('End State')
		while self.end_state not in Transition.states:
			self.end_state = self.GetInput('End State')

		self.end_symbol = self.GetInput('End Symbol')
		while self.end_symbol not in Transition.tape_alphabet:
			self.end_symbol = self.GetInput('End Symbol')

		self.direction = self.GetDirection()

	def PrintTransition(self, file: TextIOWrapper) -> None:

		file.write(
			f'{self.start_state},{self.start_symbol},{self.end_state},{self.end_symbol},{self.direction}\n'
		)

def GetTransitions() -> list[Transition]:

	transitions = []

	cont = 'y'

	while cont != 'n':

		transition = Transition()
		transition.GetUserTransition()
		transitions.append(transition)
		cont = input('Continue? (y/n): ')

	return transitions

file_name = input('TM file name: ')

with open(file_name, 'w') as file:

	# == Get symbols == #
	blank_symbol = input('\nEnter the symbol to use for blank (leave blank to use "BLANK"): ')
	if blank_symbol == '':
		blank_symbol = 'BLANK'

	tape_alphabet = [blank_symbol,]	
	print('\nEnter tape symbols one at a time, excluding the blank symbol.')
	print('Enter nothing to end.')

	symbol = input('> ')
	while symbol != '':
		tape_alphabet.append(symbol)
		symbol = input('> ')

	# == Write symbols == #
	file.write(f'Alphabet:\n')

	for symbol in tape_alphabet:
		if symbol == tape_alphabet[-1]:
			file.write(f'{symbol}\n')
		else:
			file.write(f'{symbol},')

	file.write(f'Blank Symbol:\n{blank_symbol}\n')

	# == Get states == #
	start_state = input('\nEnter the start state: ')
	while start_state == '':
		start_state = input('Start state cannot be empty: ')

	states = [start_state,]
	print('\nEnter the rest of the states one at a time.')
	print('Enter nothing to continue.')

	state = input('> ')
	while state != '':
		states.append(state)
		state = input('> ')

	# == Write states == #
	file.write('States:\n')

	for state in states:
		if state == states[-1]:
			file.write(f'{state}\n')
		else:
			file.write(f'{state},')

	Transition.SetClassVars(tape_alphabet, states)

	file.write(f'Start State:\n{start_state}\n')
	file.write('Transitions:\n')

	print('\nEnter transitions...')
	transitions = GetTransitions()
	for transition in transitions:
		transition.PrintTransition(file)

	print(f'\nTM written to {file_name}!\n')
