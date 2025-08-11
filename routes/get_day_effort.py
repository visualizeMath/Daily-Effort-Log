import sqlite3
from flask import Blueprint, jsonify, request
from  global_vars import calculate_total_effort, db_path

get_day_effort_bp = Blueprint('get_day_effort', __name__) 

@get_day_effort_bp.route('/get_day_effort',methods=['POST'])
def get_day_effort():
    try:
        data = request.json
        selected_date = data.get('selected_date')
        # print('gelen deger sprint: '+sprint_no)
        effort=calculate_total_effort(selected_date)      

        # Return the task IDs as JSON
        return jsonify(effort),200
    except Exception as e:
        print(f"Error fetching effort for selected date: {e}")
        return jsonify({'error': str(e)}), 500
