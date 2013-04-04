from model.forum import Forum
from db.query import Query
from library import cache, load

def index(Session):
	return 'this is content on a page thanks for stopping by!<br /><br />' + repr(Session.web.request)
