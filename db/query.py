import importlib
import configparser
import sys
import os

# INI Loader
ini = configparser.ConfigParser()
ini.read(os.path.join(os.path.abspath(os.path.dirname(__file__) + '/..'), 'cfg.ini'))

# Load appropriate SQL driver
importlib.import_module('db.' + ini.get('database', 'driver'))
Driver = getattr(sys.modules['db.' + ini.get('database', 'driver')],'Driver')

class Query(Driver): pass