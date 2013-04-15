from model.pytova import Pytova

class ControlAccount(Pytova):

	def get(self):
		super().get({
			'': self.index,
			'timezone': self.timezone,
			'test': self.test
		})


	def index(self):
		self.output = '<a href="'+self.url('/account/test')+'">redirect test</a> the my accounts page' + repr(self.request)

	def timezone(self):
		self.user('time_offset', int(self.get_argument('time_offset', default=None)))
		return False

	def test(self):
		self.redirect('/')