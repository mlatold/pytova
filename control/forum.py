from model.pytova import Pytova
from datetime import datetime, timedelta

class ControlForum(Pytova):

	def get(self):
		super().get({
			'': self.index
		})

	def index(self):
		self.output =  ' ' + self.date(datetime.now() + timedelta(days=5)) + 'this is content on a page thanks for stopping by!<br /><br />' + repr(self.request)