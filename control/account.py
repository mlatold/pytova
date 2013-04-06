from model.pytova import Pytova
import tornado.web

class ControlAccount(Pytova):
	def index(self):
		return 'the my accounts page'

	def get(self):
		self.output = "test"
		super().get()