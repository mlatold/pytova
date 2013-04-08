from model.pytova import Pytova

class ControlAccount(Pytova):

	def get(self):
		super().get({
			'': self.index
		})


	def index(self, test='what'):
		self.output = 'the my accounts page' + test