from flask import request,flash,jsonify,Blueprint
from global_vars import db_path
import sqlite3
from global_vars import get_tasks_for_sprint

get_total_effort_of_day_bp = Blueprint('get_total_effort_of_day_bp', __name__) 

@get_total_effort_of_day_bp.route('/get_total_effort',methods=['POST'])

def get_total_effort():
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
