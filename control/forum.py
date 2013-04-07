from model.pytova import Pytova

class ControlForum(Pytova):

	def get(self):
		{
			'': self.index
		}.get(self.uri[2], self.write_error)()
		super().get()

	def index(self):
		self.output = 'this is content on a page thanks for stopping by!<br /><br />' + repr(self.request)