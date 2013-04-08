#!/usr/bin/env python3.2
"""Pytova - A Python Forum Software
https://github.com/mikelat/pytova
Created by: Michael Lat

Licenced under GPL v3: http://www.gnu.org/licenses/gpl-3.0.txt
"""

VERSION = 'pre-alpha'

import sys
import os

import tornado.websocket
import tornado.ioloop
import tornado.web

from model.pytova import Pytova, ini
from control import *

class StaticHandler(tornado.web.StaticFileHandler):
	"""HTTP Server Static File Handler"""
	def set_extra_headers(self, path):
		self.set_header("Server", "Pytova/Tornado")

routes = []
for file in os.listdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "control"))):
	if file.endswith('.py') and file != '__init__.py':
		routes.append((r"/" + file[:-3] + ".*", getattr(sys.modules['control.' + file[:-3]], "Control" + file[:-3].title())))

webserver = tornado.web.Application(routes + [
	(r'/static/([a-zA-Z0-9_\./]*)', StaticHandler, {'path': './static/'}), # Static assets
	(r'/', forum.ControlForum), # Default page
	(r'.*', Pytova) # 404 handler
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