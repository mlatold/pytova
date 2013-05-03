from db.query import Query

class Member():
	_data = {}

	def __init__(self, **args):
		if len(args) > 0:
			self.__data = Query('member', select='*', where=args).row()
			if self._data is None:
				self._data = {}

	def __getattr__(self, name):
		if name in self._data:
			return self._data
		elif name in self:
			return self[name]
		else:
			return None

	def exists(self):
		"""Checks if we returned a member or not"""
		return bool(self._data.get('member_id'))