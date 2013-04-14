import os
import re
import json
import html
import uuid
import inspect
import traceback
import configparser
import time
from datetime import datetime, timedelta, date

import tornado.template
import tornado.web

from library import cache
from db.query import ini
import time
import http.client

cache.add('configuration', select='name, value')

# Lanuage Config
LANGUAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../lang"))
language_loader = {}
sessions = {}

# Template Loader
template_loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../view"), autoescape=None)

class Pytova(tornado.web.RequestHandler):
	"""Pytova Master Controller

	Other pages extend this controller to render their own pages (I prefix
	everything with underscores so that it doesn't conflict, since pytova
	methods accessed from web can't start with a underscore)

	As an object, everything in here is contextual to the user's request/session
	"""

	session_id = None
	spider_url = ""
	navigation = []
	language = "en"
	updated = None
	output = ""
	spider = False
	title = None
	uri = ()

	js_static = {}
	js_files = {}
	js = {}

	__baseurl = cache.get('configuration', 'url').strip('/') + '/'
	__timer = None
	__invalidurlchars = re.compile(r'[^a-z0-9\./:_]', re.I)

	def __init__(self, application, request, **kwargs):
		global sessions, template_loader, language_loader, LANGUAGE_PATH
		super().__init__(application, request, **kwargs)

		# Reload langs/templates if they're not populated, or if we're in debug mode
		if self.settings.get("debug") or len(lng) == 0:
			template_loader.reset()
			language_loader = {}
			for file in os.listdir(LANGUAGE_PATH):
				if file.endswith('.ini'):
					language_loader[file[:-4]] = configparser.ConfigParser()
					language_loader[file[:-4]].read(os.path.join(LANGUAGE_PATH, file))
		self.__timer = time.time()

		# Check for valid session
		self.session_id = self.get_cookie('session_id')
		if (self.session_id in sessions and
				(self.request.remote_ip != sessions[self.session_id]['remote_ip'] or
				self.request.headers.get('User-Agent', '') != sessions[self.session_id]['user_agent'] or
				datetime.now() - timedelta(minutes=int(15)) > sessions[self.session_id]['updated'])):
			self.session_id = None

		# Guess base URL if one isn't defined by admin
		if self.__baseurl == "/":
			self.__baseurl = self.__invalidurlchars.sub('', self.request.protocol + "://" + self.request.host).strip('/') + '/'
		self.js_static['url'] = self.__baseurl

		# Creating a session ID
		if self.session_id == None or not self.session_id in sessions:
			if cache.get('configuration', 'spiders_enabled'):
				agent = self.request.headers.get('User-Agent', '').lower()
				for spiderslist in cache.get('configuration', 'spiders_list').splitlines():
					spider = spiderslist.split(',')
					if agent.find(spider[0].lower()) >= 0:
						self.session_id, self.spider_url = spider
						self.spider = True
						break
			if self.session_id == None:
				self.session_id = str(uuid.uuid4())
				self.set_cookie('session_id', self.session_id)
		sessions.setdefault(self.session_id, {
			'new': True,
			'spider': self.spider,
			'remote_ip': self.request.remote_ip,
			'user_agent': self.request.headers.get('User-Agent', ''),
			'settings': { 'time_offset': int(time.altzone / 60 * -1), 'time_24': False }
		})['updated'] = datetime.now()

		# Parse URI argument into a tuple (minimum 3 length for convenience)
		uri = '/' + str(self.request.uri).strip('/').lower()
		if uri == '/':
			uri = '/forum/'
		while uri.count('/') < 2:
			uri += '/'
		self.uri = tuple(uri.split('/'))

		# Initalize navigation (breadcrumbs, mainly)
		self.navigation.append(("Pytova", self.__baseurl))

	def post(self):
		self.get()

	def get(self, methodlist={}):
		"""Called by tornado, meant to be overridden by parent controllers"""
		out = False
		if self.output == "":
			method = methodlist.get(self.uri[2], self.write_error)
			out = method(*self.uri[3:len(inspect.getfullargspec(method).args) + 2])

		if self._finished or out == False:
			return
		elif type(out) is str:
			self.output += out

		self.js_static['yesterday'] = self.word("yesterday", raw=True)
		self.js_static['tommorow'] = self.word("tommorow", raw=True)
		self.js_static['today'] = self.word("today", raw=True)
		self.js_static['time_24'] = self.user('time_24')
		self.js_static['time_offset'] = self.user('time_offset')
		self.js_static['url'] = self.__baseurl

		self.write(self.view('wrapper',
			output=False,
			content=self.output,
			year=date.today().year,
			on={self.uri[1]:' class="on"'},
			js=json.dumps(self.js, separators=(',', ':')),
			js_static=json.dumps(self.js_static, separators=(',', ':')),
			render=self.word('render', 'debug', time=time.time() - self.__timer)
		))

	def date(self, unix):
		"""Returns formatted HTML date tag"""
		if type(unix) is datetime:
			unix = time.mktime(unix.timetuple())
		day = datetime.utcfromtimestamp(unix) + timedelta(minutes=self.user('time_offset'))

		if self.user('time_24'):
			stime = day.strftime("%H:%M").lstrip('0')
		else:
			stime = day.strftime("%I:%M%p").lstrip('0').lower()

		if day.date() == datetime.today().date(): # Today
			out = self.word("today", time=stime)
		elif day.date() ==  (datetime.today() - timedelta(days=1)).date(): # Yesterday
			out = self.word("yesterday", time=stime)
		elif day.date() ==  (datetime.today() + timedelta(days=1)).date(): # Tommorow
			out = self.word("tommorow", time=stime)
		else:
			out = day.strftime("%Y-%m-%d " + stime)
		return  '<time datetime="' + datetime.utcfromtimestamp(unix).strftime("%Y-%m-%d %H:%M") + 'Z" data-unix="' + str(int(unix)) + '">' + out + '</time>'

	def user(self, name, value=None, fallback=None):
		global sessions
		if value != None:
			sessions[self.session_id]['settings'][name] = value
		return sessions[self.session_id]['settings'].get(name, fallback)

	def view(self, file, output=True, **args):
		"""Loads template using Tornados Template Engine"""
		global template_loader
		out = template_loader.load(file + ".html").generate(url=self.url, word=self.word, date=self.date, escape=html.escape, **args)
		if output == False:
			return out
		else:
			self.output += out

	def url(self, url=""):
		"""Returns a formatted url"""
		if url[-1:] != "/" and url != "":
			url += "/"
		return self.__baseurl + url

	def session(self, name, session_id=None, fallback=None):
		"""Grabs variable stored in session"""
		global sessions
		if session_id == None:
			session_id = self.session_id
		return sessions[session_id].get(name, fallback)


	def word(self, word, scope='global', fallback='---', raw=False, **args):
		"""Returns a formatted word from the language file"""
		global language_loader
		word = language_loader[self.language].get(scope, word, raw=True, fallback=fallback)
		if raw:
			return word
		else:
			return word.format(**args)

	def set_extra_headers(self, path):
		"""Set default headers"""
		self.set_header("Server", "Pytova/Tornado")
		self.set_header("Expires", "Sat, 1 Jan 2000 01:00:00 GMT")
		self.set_header("Cache-control", "no-cache, must-revalidate")

	def write_error(self, status_code=404, scope='global', **kwargs):
		"""Global Error handler"""
		if self.settings.get("debug") and "exc_info" in kwargs:
			self.output = self.view('error', output=False, message='<br />'.join(traceback.format_exception(*kwargs["exc_info"])))
		else:
			self.output = self.view('error', output=False, message=self.word('error_' + str(status_code), scope, fallback=str(status_code) + ': ' + http.client.responses.get(status_code, '')))