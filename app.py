import tornado.ioloop
import tornado.web
import tornado.websocket

class WebHandler(tornado.web.RequestHandler):
	def get(self):
		self.write(repr(self.request))

class SocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print 'newconnection'

	def on_message(self, message):
		print 'message: %s' % message

	def on_close(self):
		print 'closed'

webserver = tornado.web.Application([
	(r'/css/([A-Za-z0-9_\.]*)', tornado.web.StaticFileHandler, {'path': './css/'}),
	(r'/js/([A-Za-z0-9_\.]*)', tornado.web.StaticFileHandler, {'path': './js/'}),
	(r"/.*", WebHandler),
], debug=True)

socketserver = tornado.web.Application([
	(r'/', SocketHandler),
], debug=True)

if __name__ == "__main__":
	webserver.listen(80)
	socketserver.listen(9876)
	tornado.ioloop.IOLoop.instance().start()