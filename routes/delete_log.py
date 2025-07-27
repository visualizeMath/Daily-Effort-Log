from flask import request,flash,jsonify,Blueprint
from global_vars import db_path
import sqlite3
from global_vars import get_tasks_for_sprint

delete_log_bp = Blueprint('delete_log_bp', __name__) 


#Delete the selected log record from db  
@delete_log_bp.route('/delete_log', methods=['POST'])
def delete_log():
    data = request.json
    task_id = data.get('task_id')
    # print('app.py icinde gelen task id: '+task_id)

    if not task_id:
        flash(f'{task_id} numaralı efor kaydi bulunamadi.', 'danger')
        return jsonify({"success": False, "error": "Task ID not provided."}), 400
        # flash(f'ID bulunamadı: {str(e)}', 'danger')
    
    try:
        # Connect to the database and delete the task
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("select yapilan_is FROM daily_log WHERE id = ?", (task_id,))
        conn.commit()
        result= cursor.fetchone()

        if result is not None and result[0]:
            effort_text=result[0]
            # print(effort_text)
            

        if not effort_text and len(effort_text)>15:
            effort_text=effort_text[:15]+' (...)'
            # print('effort text: '+effort_text)

        cursor.execute("DELETE FROM daily_log WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        # Check if a row was actually deleted
        if cursor.rowcount == 0:
            flash(f'Silinecek kayit bulunamadi: {str(e)}', 'danger')
            return jsonify({"success": False, "error": "Log not found."}), 404
        # flash('Silindi: {effort_text}!', 'success')
        flash(f'Silindi: {effort_text}', 'success')
        return jsonify({"success": True}), 200
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return jsonify({"success": False, "error": str(e)}), 500
        # return redirect(url_for('show_logs'))
