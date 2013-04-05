import uuid
from datetime import datetime, timedelta
from library import cache
import re

class Session:
	"""This is a session object that contains all the relative information
	about the visitor accessing the site and any methods assosiated with them.

	It is important to pass it around when trying to get contextual data
	about the current user accessing the site"""
	validuri = re.compile(r'^[a-z][a-z_]*$')

	sessionid = None
	updated = None
	agent = None
	web = None
	ip = None

	spider = False
	uri = []

	def __init__(self, web):
		self.sessionid = str(uuid.uuid4())
		self.web = web
		self.web.set_cookie('sessionid', self.sessionid)

	def __setattr__(self, name, value):
		if name == 'web':
			self.updated = datetime.now()
			self.ip = value.request.remote_ip
			self.agent = value.request.headers['User-Agent']
			self.uri = str(value.request.uri).split('/')

			# Accessing default url, go to default page
			if len(self.uri) <= 1:
				self.uri = ['', 'forum', 'index']
			# Has at least the page
			else:
				self.uri[1] = self.uri[1].replace('-', '_').lower()
				if not self.validuri.match(self.uri[1]):
					self.uri = ['', 'forum', 'index']

				# Has a function argument
				if len(self.uri) >= 3:
					self.uri[2] = self.uri[2].replace('-', '_').lower()
					# Starting with a number makes it a view function
					if self.uri[2][:1].isdigit():
						self.uri.insert(2, 'view')
					# Invalid second arg directs to index
					elif not self.validuri.match(self.uri[2]):
						self.uri[2] = 'index'
				else:
					self.uri.append('index')

		super().__setattr__(name, value)

	def get(self, value):
		self.counter = 7
		return ''

	def valid(self, web):
		# Spiders bypass all checks
		if self.spider == True:
			return True
		# Check if incoming IP address and useragent match Session
		if self.ip != web.request.remote_ip or self.agent != web.request.headers['User-Agent']:
			return False
		# Check if Session Expired
		if datetime.now() - timedelta(minutes=int(cache.get('configuration', 'sessionlength'))) > self.updated:
			return False
		return True