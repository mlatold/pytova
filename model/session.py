import re

class Session:
	request = None
	uri = []

	def __setattr__(self, name, value):
		if name == 'request':
			self.uri = str(value.uri).split('/')

			# Accessing default url, go to default page
			if len(self.uri) <= 1:
				self.uri = ['', 'forum', 'index']
			# Has at least the page
			else:
				self.uri[1] = self.uri[1].replace('-', '_').lower()
				if not re.match(r'^[a-z][a-z_]*', self.uri[1]):
					self.uri = ['', 'forum', 'index']

				# Has a function argument
				if len(self.uri) >= 3:
					self.uri[2] = self.uri[2].replace('-', '_').lower()
					# Starting with a number makes it a view function
					if self.uri[2][:1].isdigit():
						self.uri.insert(2, 'view')
					# Invalid second arg directs to index
					elif not re.match(r'^[a-z][a-z_]*', self.uri[2]):
						self.uri[2] = 'index'
				else:
					self.uri.append('index')

		super().__setattr__(name, value)

	def get(self, value):
		self.counter = 7
		return ''