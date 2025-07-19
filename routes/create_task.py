import sqlite3
from flask import Blueprint, render_template 
import global_vars

create_task_bp = Blueprint('create_task_bp', __name__) 

@create_task_bp.route('/create_new_task')
def create_new_task():
    conn = sqlite3.connect( global_vars.db_path)
    c = conn.cursor()

    c.execute('SELECT max(sprint_no) son_sprint from sprints')
    max_sprint=c.fetchone()

    return render_template('create_new_task.html',max_sprint=int(max_sprint[0]))

