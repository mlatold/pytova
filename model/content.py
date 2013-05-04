from db.query import Query

class Content:
	_data = {}
	exists = False

	def __init__(self, table, dict_where={}, **args):
		if dict_where or len(args) > 0:
			if dict_where:
				args = dict_where
			content_query = Query(table, select='*', where=args).row()
			self.exists = bool(content_query)
			if self.exists:
				self._data = content_query

	def __getattr__(self, name):
		if name in self._data:
			return self._data[name]
		try:
			return self[name]
		except:
			return None

	def __setattr__(self, name, value):
		if name in self._data:
			self._data[name] = value
		else:
			super().__setattr__(name, value)