from model.pytova import Pytova
import inspect

class ControlAccount(Pytova):

	def get(self, method={}):
		super().get({
			'': self.index
		})


	def index(self, test='what'):
		self.output = 'the my accounts page' + test