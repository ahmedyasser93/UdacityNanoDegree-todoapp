from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:910172@localhost:5432/todoapp' #specify the database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
class Todo(db.Model): #create a class that represents a table in the database
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(),nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'),nullable=False)
    def __repr__(self):
        return f'<Todo: {self.id}, {self.description}>'

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.Relationship('Todo', backref='list', lazy=True, cascade='all, delete-orphan')
    def __repr__(self):
        return f'<TodoList: {self.id}, {self.name}>'
    
#When using AJAX request
@app.route('/lists/create',methods=['POST'])
def create_list():
    error=False
    body={}
    try:
        name =request.get_json()['name'] #get the description from the request body
        List=TodoList(name=name)
        db.session.add(List)
        db.session.commit()
        body['name']=List.name        
    except:
        error=True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if not error:
            return jsonify(body)
        else:
            abort(400)

@app.route('/todos/<todo_id>/delete',methods=['DELETE'])
def delete(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        return jsonify({ 'success': True })

@app.route('/lists/<list_id>/delete',methods=['DELETE'])
def deleteList(list_id):
    try:
        List = TodoList.query.get(list_id)
        db.session.delete(List)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        return jsonify({ 'success': True })

@app.route('/todos/<todo_id>/set-completed',methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo=Todo.query.get(todo_id)
        todo.completed=completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/lists/<list_id>/set-completed',methods=['POST'])
def set_completed_list(list_id):
    try:
        checkedList=TodoList.query.get(list_id)
        for todo in checkedList.todos:
            todo.completed=True
        
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))
#When using AJAX request
@app.route('/todos/create',methods=['POST'])
def create_todo():
    error=False
    body={}
    try:
        description =request.get_json()['description'] #get the description from the request body
        list_id =request.get_json()['list_id'] #get the list-id from the request body
        todo=Todo(description=description, list_id=list_id)
        db.session.add(todo)
        db.session.commit()
        body['description']=todo.description        
    except:
        error=True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if not error:
            return jsonify(body)
        else:
            abort(400)
            


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html',
     lists=TodoList.query.all(),
     active_list=TodoList.query.get(list_id),
     todos= Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/')
def index():
    return redirect(url_for('get_list_todos',list_id=2))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug =true)