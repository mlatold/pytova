from db.query import Query
queries = {}

'''
	Adds a cache
'''
def add(name, *args, **dicts):
	global queries
	queries[name] = { 'args': args, 'dicts': dicts, 'data': {} }
	reload(name)

'''
	Get a cache item
'''
def get(name, var):
	global queries
	if var in queries[name]['data']:
		return queries[name]['data'][var]
	else:
		return None

'''
	Force a reload on a cache
'''
def reload(name=''):
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
		# Complex Cache
		else:
			if 'key' not in queries[name]:
				queries[name]['key'] = list(result[0])[-1]
			for r in result:
				queries[name]['data'][r[queries[name]['key']]] = r

add('configuration', 'configuration', select='name, value')