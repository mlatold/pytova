from model.pytova import Pytova

import urllib.parse
import tornado.web
import tornado.escape

PERSONA_URL = 'https://browserid.org/verify'

class ControlAccount(Pytova):
	def get(self):
		super().get({
			'': self.index,
			'timezone': self.timezone,
			'persona': self.persona
		})

	def index(self):
		self._js_files.extend(['https://browserid.org/include.js', '/account.js'])
		self.view("account/login")

	def timezone(self):
		self.user('time_offset', int(self.get_argument('time_offset', default=None)))
		return False

	@tornado.web.asynchronous
	def persona(self):
		global PERSONA_URL
		http_client = tornado.httpclient.AsyncHTTPClient()
		response = http_client.fetch(PERSONA_URL,
			method='POST',
			body=urllib.parse.urlencode({
				'assertion': self.get_argument('assertion'),
				'audience': self.url(),
			}),
			callback=self.async_callback(self.persona_response)
		)
		return False

	def persona_response(self, response):
		struct = tornado.escape.json_decode(response.body)
		print('DEBUGGGINGGGGG', repr(struct))
		if struct['status'] != 'okay':
			raise tornado.web.HTTPError(400, "Failed assertion test")
		email = struct['email']
		#self.set_secure_cookie('user', email, expires_days=1)
		self.write('test')
		self.finish()