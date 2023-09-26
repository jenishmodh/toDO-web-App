from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import random
import string

todos = pd.read_csv("to_do_list.csv")

def assign_taskid():
    task_ids = todos['task_id'].to_list()
    id_length = 5
    characters = string.ascii_lowercase + string.digits
    while True:
        new_id = 't'+''.join(random.choice(characters) for _ in range(id_length))
        if new_id not in task_ids:
            return new_id


def due_status(due_date):
    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    if due_date == today:
        return 'Due today'
    elif due_date > today:
        return 'On time'
    elif due_date < today:
        return 'Past due'


app = Flask(__name__)


@app.route('/')
def index():

    # Update tasks' due_status whenever user visits the home page
    todos['due_status'] = todos['due_date'].apply(due_status)
    return render_template("index.html", todos=todos.to_dict(orient='records'))


@app.route('/add_task', methods=['POST'])
def add_task():
    item = request.form.get('task')
    create_date = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    due_date = request.form.get('due_date')
    status = 'open'
    task_id = assign_taskid()
    due_status = ''
    todos.loc[len(todos)] = [item, create_date, due_date, status, task_id, due_status]
    todos.to_csv("to_do_list.csv", index=False)
    return redirect(url_for('index'))


@app.route('/update_todo/', methods=['POST'])
def update_todo():
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
    todos.to_csv("to_do_list.csv", index=False)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
