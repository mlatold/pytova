from model.pytova import Pytova
from model.member import Member
from model.form import Form

import urllib.parse
import tornado.web
import tornado.escape

PERSONA_URL = 'https://verifier.login.persona.org/verify'

class ControlAuth(Pytova):
	def get(self):
		self.breadcrumb(self.word('sign_in'), "/auth")
		super().get({
			#'': self.index,
			'sign_out': self.sign_out,
			'persona': self.persona,
			'new': self.new
		})

	def sign_out(self):
		"""Process log out"""
		self.redirect('/', fmt='html')

	def new(self, email=''):
		"""Sign up page"""
		form = Form("Sign Up")

		if self.request.method == 'POST':
			print('post')

		self.view("account/sign_up", email=tornado.escape.url_unescape(email))

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

	def persona_response(self, response=None):
		"""Parse persona response"""
		struct = tornado.escape.json_decode(response.body)
		if struct['status'] == 'okay' and struct['audience'] == self.url():
			self.sign_in(email=struct['email'])
		else:
			self.write({'success': False})
			self.finish()

	def sign_in(self, email):
		user = Member({ 'member_email LIKE': email })
		if user.exists:
			self.session()['member'] = user
			self.redirect('/', success=True, header=True, fmt='json')
		else:
			self.redirect('/auth/new/' + tornado.escape.url_escape(email), success=True, fmt='json')