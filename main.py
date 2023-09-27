from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import random
import string
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Replace with your own secret key
bcrypt = Bcrypt(app)

def initialize_database():
    connection = sqlite3.connect('todo_app.db')
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, task TEXT, create_date TEXT, due_date TEXT, status TEXT, due_status TEXT)")
    connection.commit()
    connection.close()

# Initialize the database at app startup
initialize_database()

# Define a user class for user authentication (not implemented here)
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Dummy user data (replace with your own user management logic)
users = []

todos = pd.DataFrame(columns=['task', 'create_date', 'due_date', 'status', 'task_id', 'due_status'])

def assign_taskid():
    task_ids = todos['task_id'].to_list()
    id_length = 5
    characters = string.ascii_lowercase + string.digits
    while True:
        new_id = 't' + ''.join(random.choice(characters) for _ in range(id_length))
        if new_id not in task_ids:
            return new_id

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check user authentication (replace with your own logic)
        user = User(username, password)
        if user.username == 'your_username' and bcrypt.check_password_hash('your_hashed_password', user.password):
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users.append(User(username, hashed_password))
        return redirect(url_for('login'))
    return render_template('register.html')

def due_status(due_date):
    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    if due_date == today:
        return 'Due today'
    elif due_date > today:
        return 'On time'
    elif due_date < today:
        return 'Past due'

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    todos['due_status'] = todos['due_date'].apply(due_status)
    return render_template("index.html", todos=todos.to_dict(orient='records'))

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' not in session:
        return redirect(url_for('login'))

    item = request.form.get('task')
    create_date = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    due_date = request.form.get('due_date')
    status = 'open'
    task_id = assign_taskid()
    due_status = ''

    connection = sqlite3.connect('todo_app.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO tasks (task_id, task, create_date, due_date, status, due_status)VALUES (?, ?, ?, ?, ?, ?)", (task_id, item, create_date, due_date, status, due_status))
    connection.commit()
    connection.close()

    return redirect(url_for('index'))

@app.route('/update_todo/', methods=['POST'])
def update_todo():
    if 'username' not in session:
        return redirect(url_for('login'))

    task_id = (request.form.get('task_id'))
    task_index = todos[todos['task_id'] == task_id].index[0]
    button_pushed = request.form.get('update_todo')
    if button_pushed == 'update':
        todos.at[task_index, 'due_date'] = request.form.get('due_date')
        todos.at[task_index, 'task'] = request.form.get('task')
    elif button_pushed == 'complete':
        todos.at[task_index, 'status'] = 'complete'
    else:
        pass

    connection = sqlite3.connect('todo_app.db')
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET task=?, due_date=?, status=?WHERE task_id=?", (request.form.get('task'), request.form.get('due_date'), todos.at[task_index, 'status'], task_id))
    connection.commit()
    connection.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
