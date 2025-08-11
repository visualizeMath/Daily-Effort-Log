import sqlite3
from flask import Blueprint, jsonify, render_template, request,flash,redirect,url_for
from  global_vars import db_path, get_taskname_for_selected_task

get_selectedtaskname_bp = Blueprint('get_selectedtaskname_bp', __name__) 

@get_selectedtaskname_bp.route('/get_selectedtaskname',methods=['POST'])
def get_selectedtaskname():
    try:
        data = request.json
        task_id = data.get('task_id')
        # print('gelen deger sprint: '+sprint_no)
        task_name=get_taskname_for_selected_task(task_id)      

        # Return the task IDs as JSON
        return jsonify(task_name),200
    except Exception as e:
        print(f"Error fetching task ID for retrieving task name: {e}")
        return jsonify({'error': str(e)}), 500