import os
import html
import configparser
import tornado.template

# Lanuage Config
LANGUAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../lang"))
language_loader = {}

# Template Loader
template_loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../view"), autoescape=None)

def reload():
	"""Reloads template and language engines"""
	global template_loader, language_loader, LANGUAGE_PATH
	template_loader.reset()
	language_loader = {}
	for file in os.listdir(LANGUAGE_PATH):
		if file.endswith('.ini'):
			language_loader[file[:-4]] = configparser.ConfigParser()
			language_loader[file[:-4]].read(os.path.join(LANGUAGE_PATH, file))

def template(template, **args):
	"""Loads template using Tornados Template Engine"""
	global template_loader
	return template_loader.load(template + ".html").generate(escape=html.escape, **args).decode("utf-8")

def word(word, scope='global', language='en', fallback='---', raw=False, **args):
	"""Returns a formatted word from the language file"""
	global language_loader
	word = language_loader[language].get(scope, word, raw=True, fallback=fallback)
	if raw:
		return word
	else:
		return word.format(**args)