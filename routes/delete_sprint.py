import sqlite3
from flask import Blueprint, app, flash, jsonify, request
import global_vars 

delete_sprint_bp = Blueprint('delete_sprint_bp',__name__)

#Delete the selected sprint 
@delete_sprint_bp.route('/delete_sprint', methods=['POST'])
def delete_sprint():
    data = request.json
    sprint_id = data.get('sprint_id')
    
    if not sprint_id:
         
        flash(f'{sprint_id} numaralı sprint bulunamadi.', 'danger')
        return jsonify({"success": False, "error": "Sprint not provided."}), 400
    
    try:
        # Connect to the database and delete the sprint
        conn = sqlite3.connect(global_vars.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM sprints WHERE sprint_no = ?", (sprint_id,))
        conn.commit()
        conn.close()

        # Check if a row was actually deleted
        if cursor.rowcount == 0:
            flash(f'{sprint_id} numaralı sprint bulunamadi.', 'danger')
            return jsonify({"success": False, "error": "Task not found."}), 404

        flash(f'{sprint_id} numaralı sprint silindi.', 'success')
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

