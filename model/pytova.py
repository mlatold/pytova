import os
import re
import html
import configparser
import tornado.template
from library import cache
from datetime import date
from db.query import ini
import time

cache.add('configuration', select='name, value')

# Lanuage Config
LANGUAGE = 'en'
LANGUAGEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../lang"))
lng = {}

# Template Loader
loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../view"), autoescape=None)

class Pytova:
	"""Pytova Master Controller

	Other pages extend this controller to render their own pages (I prefix
	everything with underscores so that it doesn't conflict, since pytova
	methods accessed from web can't start with a underscore)

	As an object, everything in here is contextual to the user's request/session
	"""
	Session = None
	DEBUG = ini.getboolean('advanced', 'debug')
	__baseurl = None
	__timer = None
	__invalidurlchars = re.compile(r'[^a-z0-9\./:_]', re.I)

	def __init__(self, Session):
		global loader, lng, LANGUAGE
		self.Session = Session
		# Reload langs/templates if they're not populated, or if we're in debug mode
		if self.DEBUG == True or not len(lng):
			# Reload templates
			loader.reset()
			# Reload languages
			lng = {}
			for file in os.listdir(LANGUAGEPATH):
				if file[-4:] == '.ini':
					lng[file[:-4]] = configparser.ConfigParser()
					lng[file[:-4]].read(os.path.join(LANGUAGEPATH, file))
		self.__timer = time.time()

	def _url(self, url=""):
		"""Returns a formatted url"""
		if self.__baseurl == None:
			self.__baseurl = cache.get('configuration', 'url')
			if self.__baseurl == "":
				self.__baseurl = self.__invalidurlchars.sub('', self.Session.web.request.protocol + "://" + self.Session.web.request.host)
			if self.__baseurl[-1:] != "/":
				self.__baseurl += "/"
		if url[-1:] != "/" and len(url):
			url += "/"
		return self.__baseurl + url

	def _view(self, file, **args):
		"""Loads template using Tornados Template Engine"""
		global loader
		return loader.load(file + ".html").generate(_url=self._url, _word=self._word, escape=html.escape, **args)

	def _word(self, word, scope='global',  **args):
		"""Returns a formatted word from the language file"""
		global lng, LANGUAGE
		return lng[LANGUAGE].get(scope, word, raw=True, fallback='---').format(**args)

	def _render(self, output):
		"""Renders final output"""
		self.Session.web.set_header("Expires", "Sat, 1 Jan 2000 01:00:00 GMT")
		self.Session.web.set_header("Cache-control", "no-cache, must-revalidate")
		return self._view('wrapper', content=output, year=date.today().year, render=self._word('render', 'debug', time=time.time() - self.__timer))

	def _404(self):
		"""Temporary 404 page, eventually will make a better one"""
		return self._render('<div style="font-size:30px;text-align:center;color:red;margin-bottom:10px;">404 page not found.</div><img src="https://dl.dropbox.com/u/121486/crazyguy.gif" style="width:100%" />')