from model.content import Content

class Member(Content):
	def __init__(self, *args, **dicts):
		super().__init__('member', *args, **dicts)