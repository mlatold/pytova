from model.forum import Forum
from db.query import Query

#hey = Query('configuration', select='*')

def index(Session):
	return repr(Query('configuration', select='*', join='left join session on session_id="test1"').get())#.get()