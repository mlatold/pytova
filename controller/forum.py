from model.forum import Forum
from db.query import Query
from library import cache, load

def index(Session):
	return repr(Session.web.request)
