#!/usr/bin/env python3.2
VERSION = 'pre-alpha'
import sys
import inspect
import os

# Tornado Modules
import tornado.ioloop
import tornado.web
import tornado.websocket

# Pytova Modules
from controller import *
from model.session import Session
from library import config

sessions = {}

''' HTTP Server '''
class WebHandler(tornado.web.RequestHandler):
	def get(self):
		global sessions

		# Check to see if our session exists
		if self.request.remote_ip not in sessions:
			sessions[self.request.remote_ip] = Session()

		sessions[self.request.remote_ip].request = self.request
		uriclass = sessions[self.request.remote_ip].uri[1]
		urifunc = sessions[self.request.remote_ip].uri[2]

		# Check if the controller and method exists
		if 'controller.' + uriclass in sys.modules and hasattr(sys.modules['controller.' + uriclass], urifunc):
			loadmethod = getattr(sys.modules['controller.' + uriclass], urifunc)
			inspectfunc = inspect.getfullargspec(loadmethod)
			output = loadmethod(sessions[self.request.remote_ip], *sessions[self.request.remote_ip].uri[2:len(inspectfunc.args) - 1])

			self.write(output)
			return

		# Did not return, must be 404
		self.write('404')

webserver = tornado.web.Application([
	(r'/css/([A-Za-z0-9_\.]*)', tornado.web.StaticFileHandler, {'path': './css/'}),
	(r'/js/([A-Za-z0-9_\.]*)', tornado.web.StaticFileHandler, {'path': './js/'}),
	(r"/.*", WebHandler),
], debug=config.ini.get('advanced', 'debug'))

''' WebSockets Server '''
class SocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print('newconnection')

	def on_message(self, message):
		print('message: %s' % message)

	def on_close(self):
		print('closed')

socketserver = tornado.web.Application([
	(r'/', SocketHandler),
], debug=config.ini.get('advanced', 'debug'))

''' Initalize Server '''
if __name__ == "__main__":
	webserver.listen(80)
	socketserver.listen(9876)
	tornado.ioloop.IOLoop.instance().start()