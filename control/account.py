from model.pytova import Pytova

class ControlAccount(Pytova):

	def get(self):
		super().get({
			'': self.index,
			'timezone': self.timezone
		})


	def index(self, test='what'):
		self.output = 'the my accounts page' + test

	def timezone(self):
		self.user('time_offset', int(self.get_argument('time_offset', default=None)))
		return False