from flask import request,flash,jsonify,Blueprint,redirect,url_for
from global_vars import db_path
import sqlite3
from global_vars import get_tasks_for_sprint
from datetime import datetime

update_effort_explanation_bp = Blueprint('update_effort_explanation_bp', __name__) 

@update_effort_explanation_bp.route('/update_effort_explanation', methods=['POST'])
def update_effort_explanation():
    data = request.get_json()
    task_id = data.get('task_id')
    new_text = data.get('new_text')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE daily_log SET yapilan_is = ? WHERE id = ?", (new_text, task_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})