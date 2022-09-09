from collections.abc import Sequence

class CrissCrossSlat(Sequence):

	STD_SLAT_LEN = 8
	BINDING_THRESH = STD_SLAT_LEN // 2

	def __init__(
		self,
		name: str,
		orientation: str,
		glues: list[str],
		color: str ='GRAY'
	) -> None:
		
		if type(name) is not str:
			raise TypeError('Tile name must be of type \'str\'!')

		if orientation not in ['N', 'E']:
			raise ValueError('Orientation must be \'N\' or \'E\'!')

		self.CheckInputGlues(glues)

		if type(color) is not str:
			color = 'GRAY'
		
		self.name = name
		self.orientation = orientation
		self.glues = glues
		self.color = color

	def __len__(self) -> int:

		return len(self.glues)

	def __getitem__(self, i: int) -> str:

		return self.glues[i]

	def __add__(self, glues: list[str]) -> None:

		self.glues += glues

	def __str__(self) -> str:

		return self.name

	def CheckInputGlues(self, glues: list[str]) -> None:

		if type(glues) is not list:
			raise TypeError('Glues must be a list!')
		elif len(glues) == 0:
			raise ValueError('Number of glues must be at least one!')
		elif len(glues) < CrissCrossSlat.STD_SLAT_LEN:
			for _ in range(CrissCrossSlat.STD_SLAT_LEN - len(glues)):
				glues.append(None)

	def SetGlues(self, glues: list[str]) -> None:

		self.CheckInputGlues(glues)
		self.glues = glues

class CrissCrossStaple(CrissCrossSlat):
	
	def __init__(self, name: str, glues: list[str], color: str = 'ORANGE') -> None:

		if len(glues) > super().STD_SLAT_LEN:
			raise Exception(f'Staples must have fewer than {super().STD_SLAT_LEN} glues!')

		super().__init__(name, 'N', glues, color)

	def __add__(self, *_: object) -> None:
		
		raise Exception('May not add glues to staples.')

class MacroTile(Sequence):

	def __init__(self, name: str, color: str, even_row: bool):

		self.name = name
		self.color = color
		self.even_row = even_row

		self.north_west = None
		self.north_east = None
		self.south_west = None
		self.south_east = None
		self.domains = None

		super().__init__()

	def __len__(self) -> int:

		return len(self.domains)

	def __getitem__(self, i: int) -> str:

		return self.domains[i]

	def __str__(self) -> str:

		return self.name

	def SetGlues(self, north_west: str, north_east: str, south_west: str, south_east: str) -> None:

		self.north_west = north_west
		self.north_east = north_east
		self.south_west = south_west
		self.south_east = south_east

		self.SetDomains()

	def SetDomains(self) -> None:

		self.domains = [
			self.north_east,
			self.north_east,
			self.north_west,
			self.north_west,
			self.south_west,
			self.south_west,
			self.south_east,
			self.south_east,
		]

class OrigamiMacrotile(MacroTile):
	"""
	Param 'position': The seed row can be thought of as an array where:
		- Position 0 is the left growth blank
		- Position 1 is the first input symbol
		- ...
		- Position (n-2) is the right growth blank
		- Position (n-1) is the right growth edge
	"""
	def __init__(self, name: str, position: int, color: str) -> None:
		
		self.position = position
		super().__init__(name, color, True)

	def SetOutput(self, glue: str):
		
		self.SetGlues(None, glue, None, None)