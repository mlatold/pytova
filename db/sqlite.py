
from db.builder import Builder

class Driver(Builder):

	raw = {}

	def __init__(self, table, **args):
		self.raw = args