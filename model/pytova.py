import os
import re
import html
import configparser
import traceback
import tornado.template
import tornado.web
from library import cache
from datetime import date
from db.query import ini
import time
import uuid
import datetime

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
	Session = None
	DEBUG = ini.getboolean('advanced', 'debug')

	sessionid = None
	updated = None
	agent = None
	web = None
	ip = None

	spiderurl = ""
	output = ""
	spider = False
	new = True
	uri = []

	__baseurl = "http://www.pytova.com:8080/"
	__timer = None
	__invalidurlchars = re.compile(r'[^a-z0-9\./:_]', re.I)

	def __init__(self, application, request, **kwargs):
		global loader, lng, LANGUAGE, sessions
		super().__init__(application, request, **kwargs)
		# Reload langs/templates if they're not populated, or if we're in debug mode
		if self.DEBUG == True or len(lng) == 0:
			loader.reset()
			lng = {}
			for file in os.listdir(LANGUAGEPATH):
				if file[-4:] == '.ini':
					lng[file[:-4]] = configparser.ConfigParser()
					lng[file[:-4]].read(os.path.join(LANGUAGEPATH, file))
		# Start timing the session
		self.__timer = time.time()
		self.sessionid = self.get_cookie('sessionid')#cache.get('configuration', 'sessionlength')
		if self.sessionid in sessions and self.spider == False and not (self.request.remote_ip != sessions[self.sessionid]['remote_ip'] or self.request.headers.get('User-Agent') != sessions[self.sessionid]['user_agent'] or datetime.now() - timedelta(minutes=int(15)) > sessions[self.sessionid]['updated']):
			self.sessionid = None
		# Check to see if our session exists
		if self.sessionid == None or not self.sessionid in sessions:
			# Checking for spiders
			if cache.get('configuration', 'spidersenabled'):
				agent = self.request.headers.get('User-Agent').lower()
				for spiderslist in cache.get('configuration', 'spiderslist').split('\n'):
					spider = spiderslist.split(',')
					if agent.find(spider[0].lower()) >= 0:
						self.spiderurl = spider[1]
						self.sessionid = spider[0]
						self.spider = True
						break
			# Create a new sessionid
			if self.sessionid == None:
				self.sessionid = str(uuid.uuid4())
		sessions.setdefault(self.sessionid, { 'spider': self.spider, 'remote_ip': self.request.remote_ip, 'user_agent': self.request.headers.get('User-Agent') })['updated'] = datetime.now()

	def get(self):
		self.write(self.view('wrapper', write=False, content=self.output, year=date.today().year, render=self.word('render', 'debug', time=time.time() - self.__timer)))

	def view(self, file, write=True, **args):
		"""Loads template using Tornados Template Engine"""
		global loader
		output = loader.load(file + ".html").generate(url=self.url, word=self.word, escape=html.escape, **args)
		if write == True:
			return output
		else:
			self.output += output

	def url(self, url=""):
		"""Returns a formatted url"""
		"""if self.__baseurl == None:
			self.__baseurl = cache.get('configuration', 'url')
			if self.__baseurl == "":
				self.__baseurl = self.__invalidurlchars.sub('', self.Session.web.request.protocol + "://" + self.Session.web.request.host)
			if self.__baseurl[-1:] != "/":
				self.__baseurl += "/"
		if url[-1:] != "/" and len(url):
			url += "/"""
		return self.__baseurl + url

	def word(self, word, scope='global',  **args):
		"""Returns a formatted word from the language file"""
		global lng, LANGUAGE
		return lng[LANGUAGE].get(scope, word, raw=True, fallback='---').format(**args)

	def set_extra_headers(self, path):
		"""Set default headers"""
		self.set_header("Server", "Pytova/Tornado")
		self.set_header("Expires", "Sat, 1 Jan 2000 01:00:00 GMT")
		self.set_header("Cache-control", "no-cache, must-revalidate")

	def write_error(self, status_code, **kwargs):
		"""Error handler"""
		print('error')
		if self.settings.get("debug") and "exc_info" in kwargs:
			# in debug mode, try to send a traceback
			self.set_header('Content-Type', 'text/plain')
			for line in traceback.format_exception(*kwargs["exc_info"]):
				self.write(line)
			self.finish()
		else:
			self.finish("<html><title>%(code)d: %(message)s</title>"
						"<body>%(code)d: %(message)s</body></html>" % {
					"code": status_code,
					"message": httplib.responses[status_code],
					})

class oldshit():




	def _render(self, output):
		"""Renders final output"""
		return

	def _404(self):
		"""Temporary 404 page, eventually will make a better one"""
		return self._render('<div style="font-size:30px;text-align:center;color:red;margin-bottom:10px;">404 page not found.</div><img src="https://dl.dropbox.com/u/121486/crazyguy.gif" style="width:100%" />')