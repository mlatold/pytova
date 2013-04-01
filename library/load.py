LANGUAGE = 'en'
import imp
import os
import tornado.template

loader = tornado.template.Loader(os.path.join(os.path.dirname(__file__), "../view"))
f, fn, des = imp.find_module(LANGUAGE, ['language'])
lng = imp.load_module(LANGUAGE, f, fn, des);

def view(file, **args):
	global loader
	return loader.load(file + ".html").generate(word=word, **args)

def word(word, scope='_global', **args):
	global lng

	if scope not in lng.words:
		return '---'
	elif word not in lng.words[scope]:
		return '---'

	return lng.words[scope][word].format(**args)

print (view('test'))