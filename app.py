#!/usr/bin/env python3.2
import sys

# Tornado Modules
import tornado.ioloop
import tornado.web
import tornado.websocket

# Pytova Modules
from controller import *
from model import session
import inspect

sessions = {}

''' HTTP Server '''
class WebHandler(tornado.web.RequestHandler):
	def get(self):
		global sessions

		# Check to see if our session exists
		if self.request.remote_ip not in sessions:
			sessions[self.request.remote_ip] = session.Session()

		sessions[self.request.remote_ip].request = self.request
		uriclass = sessions[self.request.remote_ip].uri[1]
		urifunc = sessions[self.request.remote_ip].uri[2]

		# Check if the controller exists
		if 'controller.' + uriclass in sys.modules:
			loadclass = getattr(sys.modules['controller.' + uriclass], uriclass.title() + 'Controller')

			# Check if the method exists
			if(hasattr(loadclass, urifunc)):
				loadfunc = getattr(loadclass, urifunc)
				inspectfunc = inspect.getfullargspec(loadfunc)

				# Too many arguments, we have to splice
				if len(inspectfunc.args) < len(sessions[self.request.remote_ip].uri) - 1 and inspectfunc.varargs == None:
					output = loadfunc(sessions[self.request.remote_ip], *sessions[self.request.remote_ip].uri[2:len(inspectfunc.args) - 1])
				# Call the controller normally
				else:
					output = loadfunc(sessions[self.request.remote_ip], *sessions[self.request.remote_ip].uri[2:])

				self.write(output)
				return

		# Did not return, must be 404
		self.write('404')

webserver = tornado.web.Application([
	(r'/css/([A-Za-z0-9_\.]*)', tornado.web.StaticFileHandler, {'path': './css/'}),
	(r'/js/([A-Za-z0-9_\.]*)', tornado.web.StaticFileHandler, {'path': './js/'}),
	(r"/.*", WebHandler),
], debug=True)

''' WebSockets Server '''
class SocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print ('newconnection')

	def on_message(self, message):
		print ('message: %s' % message)

	def on_close(self):
		print ('closed')

socketserver = tornado.web.Application([
	(r'/', SocketHandler),
], debug=True)

''' Initalize the Server '''
if __name__ == "__main__":
	webserver.listen(80)
	socketserver.listen(9876)
	tornado.ioloop.IOLoop.instance().start()