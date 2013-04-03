from db.builder import Builder
from db.query import ini
import sqlite3
import re
connection = None

class Driver(Builder):
	query = ''
	args = []
	dicts = {}
	data = []
	shutdown = False
	obj = None

	'''
		Create instance of Query
	'''
	def __init__(self, query='', shutdown=False, *args, **dicts):
		# Empty Dict means it's a raw query
		if len(dicts) <= 0:
			self.query = query
			self.data = args
		# Use query builder otherwise
		else:
			if 'join' not in dicts:
				dicts['join'] = []
			elif not isinstance(dicts['join'], list):
				dicts['join'] = [dicts['join']]
			dicts['join'].insert(0, query)
			self.query, self.data = Driver.build(dicts)
		self.args = args
		self.dicts = dicts
		self.shutdown = shutdown

	'''
		Connect to a database and return a connection
	'''
	@staticmethod
	def connect():
		global connection
		if connection == None:
			connection = sqlite3.connect(ini.get('database', 'file'))
			connection.row_factory = Driver.dict_factory
			connection.text_factory = str
		return connection

	'''
		Execute a database query
	'''
	def execute(self, doclose=True):
		if self.obj == None:
			driver = self.connect()
			csr = driver.cursor()
			#print(self.query, 'test')
			#start_time = time.time()
			csr.execute(self.query, self.data)
			self.obj = csr
			driver.commit()
		self.close(doclose)
		return self.obj

	'''
		Get all rows
	'''
	def get(self, doclose=True):
		result = self.execute(False).fetchall()
		self.close(doclose)
		return result

	'''
		Get one rows
	'''
	def row(self, doclose=True):
		result = self.execute(False).fetchone()
		self.close(doclose)
		return result

	'''
		Counts number of rows
	'''
	def num(self, doclose=True):
		result = self.execute(False).rowcount()
		self.close(doclose)
		return result

	'''
		Close a cursor
	'''
	def close(self, doclose=True):
		if doclose:
			self.obj.close()