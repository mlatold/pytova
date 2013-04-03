LANGUAGE = 'en'
import os
import imp
import html
import tornado.template
from library import cache
from db.query import ini as rawini

# Language Loader
loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../view"), autoescape=None)
f, fn, des = imp.find_module(LANGUAGE, ['language'])
lng = imp.load_module(LANGUAGE, f, fn, des);

cache.add('configuration', select='name, value')

def ini(section, option):
	return rawini.get(section, option)

def config(var):
	return cache.get('configuration', var)

def view(file, **args):
	global loader
	# For some reason Tornado doesn't reload templates while in debug mode, so I do it manually here
	if ini('advanced', 'debug'):
		loader.reset()
	return loader.load(file + ".html").generate(config=config, word=word, escape=html.escape, **args)

def word(word, scope='_global', **args):
	global lng

	if scope not in lng.words:
		return '---'
	elif word not in lng.words[scope]:
		return '---'

	return lng.words[scope][word].format(**args)
