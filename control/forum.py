from db.query import Query
from model.pytova import Pytova
from library import cache

class ControlForum(Pytova):
	def index(self):
		return 'this is content on a page thanks for stopping by!<br /><br />' + repr(self.Session.web.request)