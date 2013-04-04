"""Loading

Generic loader for templates, languages, configuration, you name it. If it can
be loaded, it's probably in here.
"""
LANGUAGE = 'en'
import os
import imp
import html
import configparser
import tornado.template
from library import cache
from db.query import ini as rawini

# Lanuage Config
LANGUAGEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../lang"))
lng = {}

# Template Loader
loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../view"), autoescape=None)

# Configuration Cache
cache.add('configuration', select='name, value')

def lang():
	"""Reloads all languages"""
	global lng, LANGUAGE
	lng = {}
	for file in os.listdir(LANGUAGEPATH):
		if file[-4:] == '.ini':
			lng[file[:-4]] = configparser.ConfigParser()
			lng[file[:-4]].read(os.path.join(LANGUAGEPATH, file))

'''
	Get a ini item
'''
def ini(section, option):
	return rawini.get(section, option)

'''
	Get a config item
'''
def config(var):
	return cache.get('configuration', var)

'''
	Loads a view from template
'''
def view(file, **args):
	global loader
	# For some reason Tornado doesn't reload templates while in debug mode, so I do it manually here
	if ini('advanced', 'debug'):
		loader.reset()
	return loader.load(file + ".html").generate(config=config, word=word, escape=html.escape, **args)

'''
	Loads a word from language file
'''
def word(word, scope='global', **args):
	global lng, LANGUAGE
	return lng[LANGUAGE].get(scope, word, raw=True, fallback='---').format(**args)
