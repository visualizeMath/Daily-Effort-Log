import sqlite3
from flask import Blueprint, flash, jsonify, request
import global_vars 

activate_sprint_bp = Blueprint('activate_sprint_bp',__name__)

#Activate the selected sprint 
@activate_sprint_bp.route('/activate_sprint', methods=['POST'])
def delete_sprint():
    data = request.json
    sprint_id = data.get('sprint_id')
    
    if not sprint_id:
         
        flash(f'{sprint_id} numaralı sprint bulunamadi.', 'danger')
        return jsonify({"success": False, "error": "Sprint not provided."}), 400
    
    try:
        # Connect to the database and activate the sprint
        conn = sqlite3.connect(global_vars.db_path)
        cursor = conn.cursor()

        cursor.execute("UPDATE sprints SET is_Active='Yes' WHERE sprint_no = ?", (sprint_id,))
        cursor.execute('''UPDATE sprints SET is_Active='No' where sprint_no <> ?'''
              ,(sprint_id,)
              )
        conn.commit()
        conn.close()

        flash(f'{sprint_id} numaralı sprint aktif sprint olarak güncellendi.', 'success')
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

