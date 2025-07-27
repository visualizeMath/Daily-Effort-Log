from flask import request,flash,jsonify,Blueprint
from global_vars import db_path
import sqlite3
from global_vars import get_tasks_for_sprint

get_dependent_task_bp = Blueprint('get_dependent_task_bp', __name__) 

@get_dependent_task_bp.route('/get_dependent_tasks',methods=['POST'])

def get_dependent_tasks():
    try:
        data = request.json
        sprint_no = data.get('sprint_no')
        # print('gelen deger sprint: '+sprint_no)
        dependent_tasks=get_tasks_for_sprint(sprint_no)      

        # Return the task IDs as JSON
        return jsonify(dependent_tasks),200
    except Exception as e:
        print(f"Error fetching task IDs: {e}")
        return jsonify({'error': str(e)}), 500
