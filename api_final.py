from flask import Flask, request
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
import datetime as dt
import mysql.connector as mysql

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
)

db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "assignments"
    )
cursor = db.cursor()

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due_date' : fields.String(required=True, description='The task Due Date'),
    'Status' : fields.String(required=True,description='Not started / fininshed / In progress')    
})

todo1 = api.model('TodoStatus', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'Status' : fields.String(required=True,description='Not started / finished / In progress')    
})

class TodoDAO(object):
    def __init__(self):
        self.todos = []

    def give_dict(self,x):
        d1 = {}
        d1['Status'] = x[3]
        d1['due_date'] = x[2]
        d1['task'] = x[1]
        d1['id'] = x[0]
        return d1

    def get(self, id):
        sql= "select * from todos where id = %s"
        val = (str(id),)
        cursor.execute(sql,val)
        return self.give_dict(cursor.fetchone())
        api.abort(404, "Todo {} doesn't exist".format(id))
    
    def get_overdue_date(self,dd):
        olist={}
        val = (dd,)
        x = 0
        cursor.execute("select * from todos where due_date = %s",val)
        self.todos = cursor.fetchall()
        for todo in self.todos:
            olist[str(x)] = self.give_dict(todo)
            x=x+1
        if(len(olist) > 0):
            return olist
        api.abort(404, "Todo doesn't exist")

    def get_overdue(self):
        x = dt.datetime.now().date()
        olist = {}
        val = (x,)
        i = 0
        cursor.execute("select * from todos where due_date < %s",val)
        self.todos = cursor.fetchall()
        for todo in self.todos:
            olist[str(i)]=self.give_dict(todo)
            i+=1
        if(len(olist) > 0):
            return olist
        api.abort(404, "Todo doesn't exist")

    def get_finished(self):
        flist = {}
        i = 0
        cursor.execute("select * from todos where Status=\'finished\'")
        self.todos = cursor.fetchall()
        for todo in self.todos:
            flist[str(i)]=self.give_dict(todo)
            i+=1
        if(len(flist) > 0):
            return flist
        api.abort(404, "Todo doesn't exist")

    def create(self, data):
        flist=[]
        val = (data['task'],data['due_date'],data['Status'])
        cursor.execute("insert into todos (task,due_date,Status) values(%s,%s,%s)",val)
        cursor.execute("select max(id) from todos")
        idval = cursor.fetchone() 
        data['id'] = idval[0]
        return data

    def update(self, id, data):
        val=(data['task'],data['due_date'],data['Status'],str(id))
        cursor.execute("update todos set task = %s,due_date =%s,Status=%s where id = %s",val)
        todo = self.get(id)
        return todo

    def update_status(self, id, data):
        val=(data['Status'],str(id))
        cursor.execute("update todos set Status = %s where id = %s",val)
        todo = self.get(id)
        return todo

    def delete(self, id):
        cursor.execute("delete from todos where id="+str(id))

DAO = TodoDAO()

@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        cursor.execute("select * from todos")
        table = cursor.fetchall()
        for todo in table:
            DAO.todos.append(DAO.give_dict(todo))
        return DAO.todos

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201

@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

@ns.route('/Status/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The Status identifier')
class TodoStatus(Resource):
    @ns.expect(todo1)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update the status given its identifier'''
        return DAO.update_status(id, api.payload)

@app.route('/overdue')
def overdue():
    '''Get the list of Overdue tasks'''
    return DAO.get_overdue()

@app.route('/finished')
def finished():
    '''Get the list of finished tasks'''
    return DAO.get_finished()

@app.route('/due')
def due():
    '''Get the list of tasks with sent due_date of format yyyy-mm-dd'''
    dd = request.args.get('due_date')
    return DAO.get_overdue_date(dd)
        
if __name__ == '__main__':
    app.run(debug=True)
