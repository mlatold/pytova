from model.pytova import Pytova

class ControlForum(Pytova):

	def get(self):
		super().get({
			'': self.index
		})

	def index(self):
		self.output = 'this is content on a page thanks for stopping by!<br /><br />' + repr(self.request)