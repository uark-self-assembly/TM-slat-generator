from typing import Union


class SequenceMapper:
	"""Obtain sequences from domains; defined by user or generically generated.
	
	TODO: User input for sequence mapping not yet supported.
	"""

	def __init__(self, sequence_map: Union[dict[str, str], None] = None):
		
		if sequence_map:
			# TODO: Utilize domain-to-sequence mapping provided by user
			raise Exception(NotImplementedError)
		else:
			self._map = None
			self._z0_sequence = 'ACAGT'
			self._z1_sequence = 'TGTCA'[::-1]
	
	def getSequenceByDomain(self, domain: str) -> str:
		
		if self._map:
			# TODO: Return sequence that corresponds to 'domain' param
			raise Exception(NotImplementedError)

		if domain and domain[-1] == '*':
			return self._z1_sequence
		else:
			return self._z0_sequence

