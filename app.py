#!/usr/bin/env python3.2
"""Pytova - A Python Forum Software
https://github.com/mikelat/pytova
Created by: Mike Lat

Licenced under GPL v3
http://www.gnu.org/licenses/gpl-3.0.txt
"""

VERSION = 'pre-alpha'

from datetime import date
import inspect
import sys
import os

import tornado.websocket
import tornado.ioloop
import tornado.web

from model.session import Session
from controller import *
from library import load
from db.query import ini

sessions = {}

class WebHandler(tornado.web.RequestHandler):
	"""HTTP Server Handler"""
	def get(self):
		global sessions

		# Reload languages if debugging
		if ini.get('advanced', 'debug'):
			load.lang()

		# Check to see if our session exists
		if self.request.remote_ip not in sessions:
			sessions[self.request.remote_ip] = Session()

		self.set_header("Expires", "Sat, 1 Jan 2000 01:00:00 GMT")
		self.set_header("Server", "Pytova/Tornado")
		self.set_header("Cache-control", "no-cache, must-revalidate")

		sessions[self.request.remote_ip].web = self
		uriclass = sessions[self.request.remote_ip].uri[1]
		urifunc = sessions[self.request.remote_ip].uri[2]

		# Check if the controller and method exists
		if 'controller.' + uriclass in sys.modules and hasattr(sys.modules['controller.' + uriclass], urifunc):
			loadmethod = getattr(sys.modules['controller.' + uriclass], urifunc)
			inspectfunc = inspect.getfullargspec(loadmethod)
			output = loadmethod(sessions[self.request.remote_ip], *sessions[self.request.remote_ip].uri[2:len(inspectfunc.args) - 1])
		# Did not return, must be 404
		else:
			output = '404'

		self.write(load.view('wrapper', content=output, year=date.today().year))

class StaticHandler(tornado.web.StaticFileHandler):
	"""HTTP Server Static File Handler"""
	def set_extra_headers(self, path):
		self.set_header("Server", "Pytova/Tornado")

webserver = tornado.web.Application([
	(r'/static/([a-zA-Z0-9_\./]*)', StaticHandler, {'path': './static/'}),
	(r"/.*", WebHandler),
], debug=ini.get('advanced', 'debug'))

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
], debug=ini.get('advanced', 'debug'))

if __name__ == "__main__":
	"""Starting the server"""
	webserver.listen(ini.get('port', 'http'))
	socketserver.listen(ini.get('port', 'socket'))
	tornado.ioloop.IOLoop.instance().start()