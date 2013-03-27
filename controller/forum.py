from model.forum import Forum
from db.query import Query

hey = Query('yo')

def index(Session):
	return 'hello world'