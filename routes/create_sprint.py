# routes/create_sprint.py
import sqlite3
from flask import Blueprint, render_template # Make sure flash, jsonify, request are imported if used in other routes within this blueprint
import global_vars

create_sprint_bp = Blueprint('create_sprint_bp', __name__) 

@create_sprint_bp.route('/create_new_sprint')
def create_new_sprint():
    conn = sqlite3.connect(global_vars.db_path)
    c = conn.cursor()

    c.execute('SELECT max(sprint_no) son_sprint from sprints')
    max_sprint = c.fetchone()
    if max_sprint and max_sprint[0] is not None:
        return render_template('create_sprint.html', max_sprint=int(max_sprint[0]))
    else:
        return render_template('create_sprint.html', max_sprint=11)