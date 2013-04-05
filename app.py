#!/usr/bin/env python3.2
"""Pytova - A Python Forum Software
https://github.com/mikelat/pytova
Created by: Michael Lat

Licenced under GPL v3
http://www.gnu.org/licenses/gpl-3.0.txt
"""

VERSION = 'pre-alpha'

import inspect
import sys
import os

import tornado.websocket
import tornado.ioloop
import tornado.web

from model.session import Session
from model.pytova import Pytova
from control import *
from db.query import ini

sessions = {}

class WebHandler(tornado.web.RequestHandler):
	"""HTTP Server Handler"""
	def get(self):
		global sessions
		self.set_header("Server", "Pytova/Tornado")
		self.set_header("Expires", "Sat, 1 Jan 2000 01:00:00 GMT")
		self.set_header("Cache-control", "no-cache, must-revalidate")
		sessionid = self.get_cookie('sessionid')
		# Check to see if our session exists
		if sessionid == None or not sessionid in sessions or not sessions[sessionid].valid(self):
			newsession = Session(self)
			sessionid = newsession.sessionid
			sessions[sessionid] = newsession
		else:
			sessions[sessionid].web = self
		uriclass = sessions[sessionid].uri[1]
		urifunc = sessions[sessionid].uri[2]
		loadmethod = None
		loadclass = None
		# Check if the controller and method exists
		if 'control.' + uriclass in sys.modules:
			loadclass = getattr(sys.modules['control.' + uriclass], "Control" + uriclass.title())(sessions[sessionid])
			if hasattr(loadclass, urifunc):
				loadmethod = getattr(loadclass, urifunc)
				inspectfunc = inspect.getfullargspec(loadmethod)
				output = loadmethod(*sessions[sessionid].uri[2:len(inspectfunc.args)])
				self.write(loadclass._render(output))
		if loadmethod == None:
			if loadclass == None:
				loadclass = Pytova(sessions[sessionid])
			self.write(loadclass._404())

class StaticHandler(tornado.web.StaticFileHandler):
	"""HTTP Server Static File Handler"""
	def set_extra_headers(self, path):
		self.set_header("Server", "Pytova/Tornado")

webserver = tornado.web.Application([
	(r'/static/([a-zA-Z0-9_\./]*)', StaticHandler, {'path': './static/'}),
	(r"/.*", WebHandler),
], debug=ini.getboolean('advanced', 'debug'))

class SocketHandler(tornado.websocket.WebSocketHandler):
	"""Socket Server Handler"""
	def open(self):
		print('newconnection')

	def on_message(self, message):
		print('message: %s' % message)

	def on_close(self):
		print('closed')

socketserver = tornado.web.Application([
	(r'/', SocketHandler),
], debug=ini.getboolean('advanced', 'debug'))

if __name__ == "__main__":
	"""Starting the server"""
	webserver.listen(ini.get('port', 'http'))
	socketserver.listen(ini.get('port', 'socket'))
	tornado.ioloop.IOLoop.instance().start()