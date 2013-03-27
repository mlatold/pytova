import importlib
import sys
from library.config import ini

# Load appropriate SQL driver
importlib.import_module('db.' + ini.get('database', 'driver'))
Driver = getattr(sys.modules['db.' + ini.get('database', 'driver')],'Driver')

class Query(Driver): pass