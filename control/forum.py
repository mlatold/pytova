from model.pytova import Pytova
from datetime import datetime, timedelta

class ControlForum(Pytova):

	def get(self):
		self.breadcrumb(self.word('forums'), "/forum")
		super().get({
			'': self.index
		})

	def index(self):
		self.output =  ('5 days from now: ' + self.date(datetime.now() + timedelta(days=5)) +
		'<br />1 day from now: ' + self.date(datetime.now() + timedelta(days=1)) +
		'<br />right now: ' + self.date(datetime.now()) +
		'<br />1 day ago: ' + self.date(datetime.now() - timedelta(days=1)) +
		'<br />5 days ago: ' + self.date(datetime.now() - timedelta(days=5)) +
		'<br /><br />this is content on a page thanks for stopping by!<br /><br />' + repr(self.request))