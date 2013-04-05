import configparser
import importlib
import sys
import os

# INI Loader
ini = configparser.ConfigParser()
ini.read(os.path.join(os.path.abspath(os.path.dirname(__file__) + '/..'), 'cfg.ini'))

# Load appropriate SQL driver
importlib.import_module('db.' + ini.get('database', 'driver'))
Driver = getattr(sys.modules['db.' + ini.get('database', 'driver')],'Driver')

class Query(Driver):
	"""This is just a class that only exists to extend the driver because it
	is interchangeable.

	It's designed to be an object that is created for each new database query.
	"""
	pass