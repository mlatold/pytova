import os
import re
import html
import uuid
import inspect
import traceback
import configparser
from datetime import datetime, timedelta, date

import tornado.template
import tornado.web

from library import cache
from db.query import ini
import time
import http.client

cache.add('configuration', select='name, value')

# Lanuage Config
LANGUAGE = 'en'
LANGUAGEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../lang"))
lng = {}
sessions = {}

# Template Loader
loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../view"), autoescape=None)

class Pytova(tornado.web.RequestHandler):
	"""Pytova Master Controller

	Other pages extend this controller to render their own pages (I prefix
	everything with underscores so that it doesn't conflict, since pytova
	methods accessed from web can't start with a underscore)

	As an object, everything in here is contextual to the user's request/session
	"""
	session_id = None
	updated = None
	spiderurl = ""
	output = ""
	spider = False
	new = True
	uri = ()

	__baseurl = cache.get('configuration', 'url').strip('/') + '/'
	__timer = None
	__invalidurlchars = re.compile(r'[^a-z0-9\./:_]', re.I)

	def __init__(self, application, request, **kwargs):
		global loader, lng, LANGUAGE, sessions
		super().__init__(application, request, **kwargs)
		# Reload langs/templates if they're not populated, or if we're in debug mode
		if self.settings.get("debug") or len(lng) == 0:
			loader.reset()
			lng = {}
			for file in os.listdir(LANGUAGEPATH):
				if file[-4:] == '.ini':
					lng[file[:-4]] = configparser.ConfigParser()
					lng[file[:-4]].read(os.path.join(LANGUAGEPATH, file))
		self.__timer = time.time()
		self.session_id = self.get_cookie('session_id')
		if self.session_id in sessions and self.spider == False and not (self.request.remote_ip != sessions[self.session_id]['remote_ip'] or self.request.headers.get('User-Agent') != sessions[self.session_id]['user_agent'] or datetime.now() - timedelta(minutes=int(15)) > sessions[self.session_id]['updated']):
			self.session_id = None
		if self.__baseurl == "/":
			self.__baseurl = self.__invalidurlchars.sub('', self.request.protocol + "://" + self.request.host).strip('/') + '/'
		# Creating a session
		if self.session_id == None or not self.session_id in sessions:
			if cache.get('configuration', 'spiders_enabled'):
				agent = self.request.headers.get('User-Agent').lower()
				for spiderslist in cache.get('configuration', 'spiders_list').splitlines():
					spider = spiderslist.split(',')
					if agent.find(spider[0].lower()) >= 0:
						self.session_id, self.spider_url = spider
						self.spider = True
						break
			# Create a new sessionid
			if self.session_id == None:
				self.session_id = str(uuid.uuid4())
				self.set_cookie('session_id', self.session_id)
		sessions.setdefault(self.session_id, { 'spider': self.spider, 'remote_ip': self.request.remote_ip, 'user_agent': self.request.headers.get('User-Agent') })['updated'] = datetime.now()
		# Parse URI argument
		uri = '/' + str(self.request.uri).strip('/').lower()
		while uri.count('/') < 2:
			uri += '/'
		self.uri = tuple(uri.split('/'))

	def get(self, methodlist={}):
		"""Called by tornado, meant to be overridden by parent controllers"""
		if self.output == "":
			method = methodlist.get(self.uri[2], self.write_error)
			method(*self.uri[3:len(inspect.getfullargspec(method).args) + 2])
		if self._finished:
			return
		self.write(self.view('wrapper', output=False, content=self.output, year=date.today().year, render=self.word('render', 'debug', time=time.time() - self.__timer)))

	def view(self, file, output=True, **args):
		"""Loads template using Tornados Template Engine"""
		global loader
		out = loader.load(file + ".html").generate(url=self.url, word=self.word, escape=html.escape, **args)
		if output == False:
			return out
		else:
			self.output += out

	def url(self, url=""):
		"""Returns a formatted url"""
		if url[-1:] != "/" and url != "":
			url += "/"
		return self.__baseurl + url

	def word(self, word, scope='global', fallback='---', **args):
		"""Returns a formatted word from the language file"""
		global lng, LANGUAGE
		return lng[LANGUAGE].get(scope, word, raw=True, fallback=fallback).format(**args)

	def set_extra_headers(self, path):
		"""Set default headers"""
		self.set_header("Server", "Pytova/Tornado")
		self.set_header("Expires", "Sat, 1 Jan 2000 01:00:00 GMT")
		self.set_header("Cache-control", "no-cache, must-revalidate")

	def write_error(self, status_code=404, scope='error', **kwargs):
		"""Error handler"""
		if self.settings.get("debug") and "exc_info" in kwargs:
			self.output = self.view('error', output=False, message='<br />'.join(traceback.format_exception(*kwargs["exc_info"])))
		else:
			self.output = self.view('error', output=False, message=self.word('error_' + str(status_code), scope, fallback=str(status_code) + ': ' + http.client.responses.get(status_code, '')))