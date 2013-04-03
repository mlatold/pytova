#!/usr/bin/env python3.2
VERSION = 'pre-alpha'
import sys
import inspect
import os
from datetime import date

# Tornado Modules
import tornado.ioloop
import tornado.web
import tornado.websocket

# Pytova Modules
from controller import *
from model.session import Session
from library import load
from db.query import ini

sessions = {}

''' HTTP Server '''
class WebHandler(tornado.web.RequestHandler):
	def get(self):
		global sessions

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

webserver = tornado.web.Application([
	(r'/css/([A-Za-z0-9_\.]*)', tornado.web.StaticFileHandler, {'path': './css/'}),
	(r'/js/([A-Za-z0-9_\.]*)', tornado.web.StaticFileHandler, {'path': './js/'}),
	(r"/.*", WebHandler),
], debug=ini.get('advanced', 'debug'))

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
], debug=ini.get('advanced', 'debug'))

''' Initalize Server '''
if __name__ == "__main__":
	webserver.listen(ini.get('port', 'http'))
	socketserver.listen(ini.get('port', 'socket'))
	tornado.ioloop.IOLoop.instance().start()