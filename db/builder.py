from db.query import ini
import re

class Builder:
	"""Generic Query Builder
	
	Contains methods for building and parsing queries that is flexible between
	potentially multipule database configurations.
	"""
	prefix = ini.get('database', 'prefix')
	tablere = re.compile(r'((left|right|inner) join )?(.+)', re.I)

	@staticmethod
	def dict_factory(cursor, row):
		"""Turns query results into dicts"""
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	@staticmethod
	def table(tablelist):
		"""Parses table names into joins and adds table prefixes"""
		result = ''
		if not isinstance(tablelist, list):
			tablelist = [tablelist]

		for table in tablelist:
			join = table[:10].lower()
			if join == 'left join ':
				result += ' LEFT JOIN ' + Builder.prefix + table[10:]
			elif join == 'right join':
				result += ' RIGHT JOIN ' + Builder.prefix + table[11:]
			elif join == 'inner join':
				result += ' INNER JOIN ' + Builder.prefix + table[11:]
			else:
				result += ' ' + Builder.prefix + table
		return result

	@staticmethod
	def sanitize(val, data):
		"""Adds data to list so that it can be sanitized with the python DB driver"""
		if isinstance(val, int):
			return val
		data += [val]
		return '?'

	@staticmethod
	def build(sql):
		"""Builds the query from a dict into an sql query and data set"""
		data = []
		query = ''
		querytype = ''

		'''
				if 'join' in sql:  # JOIN
					for join, table, on in sql['join']:
						query += ' ' + join + ' JOIN ' + Builder.prefix(table) + ' ON ' + on

				if 'set' in sql:  # SET
					setq = []
					for key, s in sql['set'].items():
						setq = setq + [key + '=' + Builder.sanitize(s, data)]
					query += ' SET ' + ', '.join(setq)

				if 'where' in sql:  # WHERE
					query += ' WHERE ' + Builder.where(sql['where'], data)

				#if 'group' in sql:  # GROUP BY
				#	query += ' GROUP BY ' + ', '.join(sql['group'])

				if 'order' in sql:  # ORDER BY
					query += ' ORDER BY ' + ', '.join(sql['order'])

				if 'limit' in sql:  # LIMIT
					query += ' LIMIT ' + ','.join([str(int(l)) for l in sql['limit']])

				if 'insert' in sql:  # INSERT
					query += ' (' + ', '.join(sql['insert'][0].keys()) + ') VALUES'
					for insert in sql['insert']:
						query += ' (' + ', '.join(str(Builder.sanitize(i, data))
												for k, i in insert.items()) + ')'
		'''

		if 'select' in sql:
			query = 'SELECT ' + sql['select'] + ' FROM' + Builder.table(sql['join'])
			
		'''
				query = {
					'select': 'SELECT'
				, 	'update': 'UPDATE'
				, 	'delete': 'DELETE FROM'
				, 	'insert': 'INSERT INTO'
				, 	'replace': 'REPLACE INTO'
				}[sql['type']] + ' ' + query
		'''
		return [query, data]

	@staticmethod
	def where(where, data, brackets=False):
		"""Parses where brackets and clauses"""
		where_string = ''

		for key, val in where.items():
			if isinstance(val, dict):
				Builder.parse_where(val, data, True)
			else:
				if where_string != '':
					if key[:3] == 'OR ':
						where_string += ' OR '
					else:
						where_string += ' AND '
				where_string += key

				if key[-1:].isalpha():
					where_string += '='

				where_string += '?'
				data += [val]

		if brackets:
			return '(' + where_string + ')'
		else:
			return where_string
