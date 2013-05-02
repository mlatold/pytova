from model.pytova import Pytova

import urllib.parse
import tornado.web
import tornado.escape

PERSONA_URL = 'https://browserid.org/verify'

class ControlAuth(Pytova):
	def get(self):
		self.navigation.append(("/auth", self.word('sign_in')))
		super().get({
			'': self.index,
			'persona': self.persona
		})

	def index(self):
		"""Sign in page"""
		self._js_files.extend(['https://browserid.org/include.js', '/auth.js'])
		self.js['persona_error'] = self.word('persona_error', 'auth')
		self.view("auth/login")

	@tornado.web.asynchronous
	def persona(self):
		"""Process persona login"""
		global PERSONA_URL
		http_client = tornado.httpclient.AsyncHTTPClient()
		response = http_client.fetch(PERSONA_URL,
			method='POST',
			body=urllib.parse.urlencode({
				'assertion': self.get_argument('assertion'),
				'audience': self.url()
			}),
			callback=self.async_callback(self.persona_response)
		)
		return False

	def persona_response(self, response):
		"""Parse persona response"""
		struct = tornado.escape.json_decode(response.body)
		if struct['status'] == 'okay' and struct['audience'] == self.url() or self.sign_in(email=struct['email']):
			self.redirect('/', success=True, header=True, fmt='json')
		else:
			self.write({'success': False})
			self.finish()

	def sign_in(self, email=""):
		return False