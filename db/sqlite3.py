from db.builder import Builder
from db.query import ini
import tornado.gen
import sqlite3
import re
import time
connection = None

class Driver(Builder):
	"""This is database driver that is isolated and loaded dynamically
	It takes defined ini variables and connects to our database accordingly.

	This class should only contain methods that are unique to sqlite3.
	Builder contains a lot of the crossover methods and query builder functions.

	Each database query is considered to be a seperate object in Pytova.
	"""
	query = ''
	args = []
	dicts = {}
	data = []
	shutdown = False
	obj = None

	def __init__(self, query='', shutdown=False, *args, **dicts):
		if len(dicts) <= 0:
			# Empty Dict means it's a raw query
			self.query = query
			self.data = args
		else:
			# Use query builder otherwise
			if 'join' not in dicts:
				dicts['join'] = []
			elif not isinstance(dicts['join'], list):
				dicts['join'] = [dicts['join']]
			dicts['join'].insert(0, query)
			self.query, self.data = Driver.build(dicts)
		self.args = args
		self.dicts = dicts
		self.shutdown = shutdown

	@staticmethod
	def connect():
		"""Returns an instance of a database connection, creates one if none exists"""
		global connection
		if connection == None:
			connection = sqlite3.connect(ini.get('database', 'file'))
			connection.row_factory = Driver.dict_factory
			connection.text_factory = str
		return connection

	def execute(self, doclose=True):
		"""Executes a database query and returns a cursor object"""
		if self.obj == None:
			driver = self.connect()
			csr = driver.cursor()
			#print(self.query)
			#start_time = time.time()
			csr.execute(self.query, self.data)
			self.obj = csr
			driver.commit()
		self.close(doclose)
		return self.obj

	def get(self, doclose=True):
		"""Returns rows as a dict"""
		result = self.execute(False)
		result = result.fetchall()
		self.close(doclose)
		return result

	def row(self, doclose=True):
		"""Returns only one row"""
		result = self.execute(False).fetchone()
		self.close(doclose)
		return result

	def num(self, doclose=True):
		"""Returns number of rows"""
		result = self.execute(False).rowcount()
		self.close(doclose)
		return result

	def close(self, doclose=True):
		"""Closes cursor"""
		if doclose:
			self.obj.close()