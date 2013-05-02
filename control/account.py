from model.pytova import Pytova

PERSONA_URL = 'https://browserid.org/verify'

class ControlAccount(Pytova):
	def get(self):
		super().get({
			'': self.index,
			'timezone': self.timezone,
		})

	def index(self):
		self.view("")

	def timezone(self):
		self.user('time_offset', int(self.get_argument('time_offset', default=None)))
		return False