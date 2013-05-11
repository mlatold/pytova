import tornado.escape
import re
from library import load

class Form:
	validation = {
		'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$'),
		'password': re.compile(r'^(?=.*(\d|\W))')
	}
	messages = {
		'email': 'Invalid Email Address',
		'password': 'Invalid Email'
	}
	request = None
	values = {}
	field = {}
	label = {}
	form = ''

	def __init__(self, name='form', language='en'):
		self.language = language
		self.form = name
		self.hidden = []

	def input(self, name, input_type='text', default=None, value=None, extra='', **attributes):
		# Set default input value
		if ('value' not in attributes or attributes['value'] == None) and default != None:
			attributes['value'] = default
		# Parse attributes
		for k, v in attributes.items():
			extra += ' ' + k + '="' + tornado.escape.xhtml_escape(v) + '"'
		# Hidden input type
		if type == 'hidden':
			self.hidden.append('<input type="hidden" name="{0}" id="{0}"{1} />'.format(name, extra))
		# Other inputs (text, date, email, etc)
		else:
			self.field.append('<input type="{1}" name="{0}" id="{0}"{2} />'.format(name, input_type, extra))