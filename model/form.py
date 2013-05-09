import tornado.escape
import re

class Form:
	validation = {
		'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$'),
		'password': re.compile(r'^(?=.*(\d|\W))')
	}
	values = {}
	field = {}
	label = {}
	hidden = []
	request = None

	def __init__(self, name='form'):
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