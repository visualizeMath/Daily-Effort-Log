from flask import request,flash,jsonify,Blueprint,render_template
from global_vars import db_path
import sqlite3
from global_vars import get_sprints_with_active_tasks


enter_log_bp = Blueprint('enter_log_bp', __name__) 

@enter_log_bp.route('/enter_log')
def enter_log():
  
    active_sprints=get_sprints_with_active_tasks()
    # print(type(active_sprints))
    # print(active_sprints[0])
    return render_template('enter_log.html', task_ids=[],active_sprints=active_sprints)

