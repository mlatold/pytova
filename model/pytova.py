import os
import re
import time
import html
import uuid
import inspect
import traceback
import configparser
import urllib.parse
from datetime import datetime, timedelta, date

import tornado.template
import tornado.escape
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
	language = "en"
	output = ""
	uri = ()

	js_static = {}
	js = {}

	__timer = None
	__invalidurlchars = re.compile(r'[^a-z0-9\./:_]', re.I)
	__baseurl = cache.get('configuration', 'url').strip('/') + '/'

	def __init__(self, application, request, **kwargs):
		global sessions, template_loader, language_loader, LANGUAGE_PATH
		super().__init__(application, request, **kwargs)
		spider_url = ""
		spider = False

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
			self.__baseurl = self.__invalidurlchars.sub('', self.request.protocol + "://" + self.request.headers.get('X-Forwarded-Host', self.request.host)).strip('/') + '/'
		self.js_static['url'] = self.__baseurl

		# Creating a session ID
		if self.session_id == None or not self.session_id in sessions:
			if cache.get('configuration', 'spiders_enabled'):
				agent = self.request.headers.get('User-Agent', '').lower()
				for spiderslist in cache.get('configuration', 'spiders_list').splitlines():
					spider = spiderslist.split(',')
					if agent.find(spider[0].lower()) >= 0:
						session_id, spider_url = spider
						spider = True
						break
			if self.session_id == None:
				self.session_id = str(uuid.uuid4())
				self.set_cookie('session_id', self.session_id)
		sessions.setdefault(self.session_id, {
			'new': True,
			'spider': spider,
			'spider_url': spider_url,
			'remote_ip': self.request.remote_ip,
			'user_agent': self.request.headers.get('User-Agent', ''),
			'settings': { 'time_offset': int(time.altzone / 60 * -1), 'time_24': False }
		})['updated'] = datetime.now()

		# Parse URI argument into a tuple (minimum 3 length for convenience)
		uri = ('/' + str(self.request.uri).strip('/').lower() + '?').split('?', 1)[0]
		if uri == '/':
			uri = '/forum/'
		while uri.count('/') < 2:
			uri += '/'
		self.uri = tuple(uri.split('/'))

		# Initalize navigation (breadcrumbs, mainly)
		self.navigation = [("Pytova", self.__baseurl)]
		self._js_files = []

	def post(self):
		"""Redirect post requests to be get requests"""
		self.get()

	def get(self, methodlist={}):
		"""Called by tornado, meant to be overridden by parent controllers"""
		out = False
		if self.output == "":
			method = methodlist.get(self.uri[2], self.write_error)
			out = method(*self.uri[3:len(inspect.getfullargspec(method).args) + 2])

		# Finished or output doesn't want us to flush buffer
		if self._finished or out == False:
			return
		# Add any strings returned to our output
		elif type(out) is str:
			self.output += out

		format = self.get_argument('fmt', default='html')

		# Add absolute URLs to javascript files
		for index, js_file in enumerate(self._js_files):
			if js_file[:1] == '/':
				self._js_files[index] = self.url('static/js').rstrip('/') + js_file

		if format == 'html':
			# Static javascript (always loaded on page)
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
				js=tornado.escape.json_encode(self.js),
				js_files=self._js_files,
				js_static=tornado.escape.json_encode(self.js_static),
				render=self.word('render', 'debug', time=time.time() - self.__timer),
				navigation=self.navigation
			))
		else:
			# URL arguments passed by redirects used in json returns
			out_dict = {}
			if self.request.uri.find('?') != -1:
				out_dict = dict(urllib.parse.parse_qsl(self.request.uri[self.request.uri.find('?') + 1:]))
				out_dict.pop('json', '')
				for k, v in out_dict.items():
					if v == "True":
						out_dict[k] = True
					elif v == "False":
						out_dict[k] = False
			# Pass current url if we redirected
			if out_dict.get('redirect') == True:
				out_dict['url'] = self.url("/".join(self.uri))
			# Page is requesting new version of the header
			if out_dict.get('header') == True:
				out_dict['header'] = self.view('header',
					output=False,
					on={self.uri[1]:' class="on"'}
				)
			out_dict.update({
				'js': self.js,
				'jsf': self._js_files,
				'out': self.output,
				'nav': self.navigation[1:]
			})
			self.write(out_dict)

	def date(self, unix):
		"""Returns formatted HTML date tag"""
		if type(unix) is datetime:
			unix = time.mktime(unix.timetuple())
		day = datetime.utcfromtimestamp(unix) + timedelta(minutes=self.user('time_offset'))

		# 24 hour formatting
		if self.user('time_24'):
			clock = day.strftime("%H:%M").lstrip('0')
		else:
			clock = day.strftime("%I:%M%p").lstrip('0').lower()

		# Relative day format
		if day.date() == datetime.today().date(): # Today
			out = self.word("today", time=clock)
		elif day.date() ==  (datetime.today() - timedelta(days=1)).date(): # Yesterday
			out = self.word("yesterday", time=clock)
		elif day.date() ==  (datetime.today() + timedelta(days=1)).date(): # Tommorow
			out = self.word("tommorow", time=clock)
		else:
			out = day.strftime("%Y-%m-%d " + clock)
		return  '<time datetime="' + datetime.utcfromtimestamp(unix).strftime("%Y-%m-%d %H:%M") + 'Z" data-unix="' + str(int(unix)) + '">' + out + '</time>'

	def session(self, name, session_id=None, fallback=None):
		"""Returns session contextual setting"""
		global sessions
		if session_id == None:
			session_id = self.session_id
		return sessions[session_id].get(name, fallback)

	def user(self, name, value=None, fallback=None):
		"""Returns user contextual setting"""
		global sessions
		if value != None:
			sessions[self.session_id]['settings'][name] = value
		return sessions[self.session_id]['settings'].get(name, fallback)

	def redirect(self, url, permanent=False, status=None, **args):
		"""Inserts base url when redirecting"""
		if url[:1] == '/':
			url = self.url(url)
			args['redirect'] = True
			if self.get_argument('fmt', default=None):
				args['fmt'] = self.get_argument('fmt')
			url += '?' + urllib.parse.urlencode(args)
		super().redirect(url, permanent, status)

	def view(self, file, output=True, **args):
		"""Loads template using Tornados Template Engine"""
		global template_loader
		out = template_loader.load(file + ".html").generate(url=self.url, word=self.word, date=self.date, escape=html.escape, **args).decode("utf-8")
		if output == True:
			self.output += out
		return out

	def url(self, url=""):
		"""Returns a formatted url"""
		return (self.__baseurl + url.lstrip("/")).rstrip("/") + "/"

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
		self.navigation = [self.navigation[0], ("/", self.word('error'))]
		if self.settings.get("debug") and "exc_info" in kwargs:
			self.output = self.view('error', output=False, message='<br />'.join(traceback.format_exception(*kwargs["exc_info"])))
		else:
			self.output = self.view('error', output=False, message=self.word('error_' + str(status_code), scope, fallback=str(status_code) + ': ' + http.client.responses.get(status_code, '')))