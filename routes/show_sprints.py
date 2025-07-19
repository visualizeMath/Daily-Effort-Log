import sqlite3
from flask import Blueprint, render_template 
import global_vars

show_sprints_bp = Blueprint('show_sprints_bp', __name__) 

@show_sprints_bp.route('/show_sprints')
def show_sprints():
    conn = sqlite3.connect(global_vars.db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM sprints order by sprint_id desc')
    sprints_all = c.fetchall()
    print(sprints_all)
    conn.close()
    return render_template('show_sprints.html', sprints=sprints_all)