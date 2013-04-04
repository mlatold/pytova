"""Cache Handling

This allows database queries to be stored as variables. Pytova is a persistant
app so this allows us to make the application slightly faster by keeping data
accessed frequently but updated sparsely in memory.
"""

from db.query import Query
queries = {}

def add(*args, **dicts):
	"""Creates a new cache entry and loads it"""
	global queries
	# Handles raw queries (first key is cache name)
	name = args[0]
	if len(dicts) <= 0:
		del args[0]
	# Create cache entry
	queries[name] = { 'args': args, 'dicts': dicts, 'data': {} }
	reload(name)

def get(name, var):
	"""Returns a entry from Cache"""
	global queries

	if var in queries[name]['data']:
		return queries[name]['data'][var]
	else:
		return None

def reload(name=''):
	"""Rexecutes a cached database query"""
	global queries
	# No argument is defined, reload the entire cache
	if name == '':
		for cachename in queries:
			Cache.reload(cachename)
			return
	queries[name]['data'] = {}
	result = Query(*queries[name]['args'], **queries[name]['dicts']).get()
	if len(result):
		# Key value relationship
		if len(result[0]) == 2:
			for r in result:
				key, value = r.values()
				queries[name]['data'][key] = value
		# Complex Cache (many values)
		else:
			if 'key' not in queries[name]:
				queries[name]['key'] = list(result[0])[-1]
			for r in result:
				queries[name]['data'][r[queries[name]['key']]] = r