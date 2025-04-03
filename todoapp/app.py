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
    def __repr__(self):
        return f'<Todo: {self.id}, {self.description}>'


"""   
with app.app_context():
    db.create_all()
"""
#When using the traditional method (No AJAX request)
""" 
@app.route('/todos/create',methods=['POST'])
def create_todo():
    description =request.form.get('description','')
    todo=Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('index')) """
    
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
#When using AJAX request
@app.route('/todos/create',methods=['POST'])
def create_todo():
    error=False
    body={}
    try:
        description =request.get_json()['description'] #get the description from the request body
        todo=Todo(description=description)
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
            


@app.route('/')
def index():
    return render_template('index.html', data= Todo.query.order_by('id').all())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)