from datetime import datetime, timedelta
from library import cache
from db.query import Query
import tornado.web
import re

sessions = {}

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

	spiderurl = ""
	spider = False
	new = True
	uri = []

	def __init__(self, web, sessionid, spiderurl=None):
		global sessions

		self.sessionid = sessionid
		if spiderurl != None:
			spider = True
			self.spiderurl = spiderurl
		else:
			self.web.set_cookie('sessionid', sessionid)

	def __setattr__(self, name, value):
		if name == 'web':
			self.updated = datetime.now()
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

	def valid(self, web):
		"""Checks if this session is still valid"""
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

	def update(self):
		# New session needs a database insert
		if self.new:
			return
