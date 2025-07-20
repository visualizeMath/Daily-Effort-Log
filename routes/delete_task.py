#Delete the selected task 
from flask import request,flash,jsonify,Blueprint
from global_vars import db_path
import sqlite3

delete_task_bp = Blueprint('delete_task_bp', __name__) 

@delete_task_bp.route('/delete_task', methods=['POST'])
def delete_task():
    data = request.json
    task_id = data.get('task_id')
    
    if not task_id:
         
        flash(f'{task_id} numaralı PDAS taskı bulunamadi.', 'danger')
        return jsonify({"success": False, "error": "Task ID not provided."}), 400
    
    try:
        # Connect to the database and delete the task
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM pdas WHERE pdas_task_id = ?", (task_id,))
        conn.commit()
        conn.close()

        # Check if a row was actually deleted
        if cursor.rowcount == 0:
            flash(f'{task_id} numaralı PDAS taskı bulunamadi.', 'danger')
            return jsonify({"success": False, "error": "Task not found."}), 404

        flash(f'{task_id} numaralı PDAS taskı silindi.', 'success')
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500