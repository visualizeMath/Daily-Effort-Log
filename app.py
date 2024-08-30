from datetime import datetime
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for
import sqlite3
import secrets
import pandas as pd

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

def init_db():
    conn = sqlite3.connect('daily_log.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS daily_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    task_aciklama TEXT,
                    tarih TEXT,
                    gun TEXT,
                    harcanan_efor REAL,
                    yapilan_is TEXT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS pdas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pdas_task_id TEXT,
                    pdas_task_aciklama TEXT,
                    bagli_sprint TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enter_log')
def enter_log():
    # conn = sqlite3.connect('daily_log.db')
    # c = conn.cursor()
    # c.execute('SELECT pdas_task_id FROM pdas')
    # task_ids = c.fetchall()  # Fetch all task IDs
    # conn.close()

    # Pass the task_ids to the template
    # return render_template('enter_log.html', task_ids=[task_id[0] for task_id in task_ids])
    return render_template('enter_log.html', task_ids=[])
@app.route('/get_dependent_tasks',methods=['POST'])
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

@app.route('/get_selectedtaskname',methods=['POST'])
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


def get_tasks_for_sprint(sprint_no):
    conn = sqlite3.connect('daily_log.db')
    c = conn.cursor()
    c.execute(f'SELECT pdas_task_id FROM pdas WHERE bagli_sprint ={sprint_no} ')
   
    dependent_tasks=[]

    for row in c.fetchall():
        # print('satir: '+row[0]+' \n')
        spNo=row[0].strip()
        if(len(spNo)>0 and spNo.isdigit()):
            dependent_tasks.append(spNo)
    conn.close()
    # dependent_tasks=dependent_tasks.sort()
    return sorted(dependent_tasks)

def get_taskname_for_selected_task(task_id):
    conn = sqlite3.connect('daily_log.db')
    c = conn.cursor()
    c.execute(f'SELECT pdas_task_aciklama FROM pdas WHERE pdas_task_id ={task_id} ')
   
    task_name=''

    for row in c.fetchall():
        current_task_name=row[0].strip()
        if(len(current_task_name)>0):
            task_name=current_task_name
    conn.close()    
    return task_name

@app.route('/create_pdas_item')
def create_pdas_item():
    return render_template('create_pdas_item.html')

@app.route('/submit_log', methods=['POST'])
def submit_log():
    task_id = request.form['task_id']
    task_aciklama = request.form.get('task_aciklama','')
    # print(request.form)
    # tarih = request.form['tarih'].format("dd.MM.YYYY")
    tarih_str = request.form['tarih']
    tarih_obj = datetime.strptime(tarih_str, '%Y-%m-%d')
    formatted_tarih = tarih_obj.strftime('%d.%m.%Y')
    gun = request.form['gun']
    harcanan_efor = request.form['harcanan_efor']
    yapilan_is = request.form['yapilan_is'].encode('utf-8').decode('utf-8')

    conn = sqlite3.connect('daily_log.db')
    c = conn.cursor()
    c.execute('''INSERT INTO daily_log (task_id, task_aciklama, tarih,gun, harcanan_efor, yapilan_is) 
                 VALUES (?, ?, ?, ?, ?, ?)''', 
                 (task_id, task_aciklama, formatted_tarih,gun, harcanan_efor, yapilan_is))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/submit_pdas_task', methods=['POST'])
def submit_pdas_task():
    pdas_task_id = request.form['pdas_task_id']
    pdas_task_aciklama = request.form['pdas_task_aciklama']
    bagli_sprint = request.form['bagli_sprint']

    conn = sqlite3.connect('daily_log.db')
    c = conn.cursor()
    c.execute('''INSERT INTO pdas (pdas_task_id, pdas_task_aciklama, bagli_sprint) 
                 VALUES (?, ?, ?)''', 
                 (pdas_task_id, pdas_task_aciklama, bagli_sprint))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/show_logs')
def show_logs():
    conn = sqlite3.connect('daily_log.db')
    c = conn.cursor()
    c.execute('SELECT * FROM daily_log')
    logs = c.fetchall()
    conn.close()
    return render_template('show_logs.html', logs=logs)

@app.route('/show_pdas_items')
def show_pdas_items():
    conn = sqlite3.connect('daily_log.db')
    c = conn.cursor()
    c.execute('SELECT * FROM pdas')
    pdas_logs = c.fetchall()
    conn.close()
    return render_template('show_pdas.html', logs=pdas_logs)

#Delete the selected pdas task 
@app.route('/delete_task', methods=['POST'])
def delete_task():
    data = request.json
    task_id = data.get('task_id')
    
    if not task_id:
        return jsonify({"success": False, "error": "Task ID not provided."}), 400
    
    try:
        # Connect to the database and delete the task
        conn = sqlite3.connect('daily_log.db')
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM pdas WHERE pdas_task_id = ?", (task_id,))
        conn.commit()
        conn.close()

        # Check if a row was actually deleted
        if cursor.rowcount == 0:
            return jsonify({"success": False, "error": "Task not found."}), 404

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


    return jsonify({'success': False, 'message': 'No entry found'}), 404

#Delete the selected log record from db  
@app.route('/delete_log', methods=['POST'])
def delete_log():
    data = request.json
    task_id = data.get('task_id')
    # print('app.py icinde gelen task id: '+task_id)

    if not task_id:
        return jsonify({"success": False, "error": "Task ID not provided."}), 400
        # flash(f'ID bulunamadı: {str(e)}', 'danger')
    
    try:
        # Connect to the database and delete the task
        conn = sqlite3.connect('daily_log.db')
        cursor = conn.cursor()

        # effort_text= cursor.execute("select yapilan_is FROM daily_log WHERE id = ?", (task_id,))
        # conn.commit()
        # if not effort_text:
        #     effort_text=effort_text[:25]+' (...)'
        #     print('effort text: '+effort_text)

        cursor.execute("DELETE FROM daily_log WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        # Check if a row was actually deleted
        if cursor.rowcount == 0:
            flash(f'Silinecek kayit bulunamadi: {str(e)}', 'danger')
            return jsonify({"success": False, "error": "Log not found."}), 404
        # flash('Silindi: {effort_text}!', 'success')

        return jsonify({"success": True}), 200
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return jsonify({"success": False, "error": str(e)}), 500
        # return redirect(url_for('show_logs'))

@app.route('/export_to_xl', methods=['GET'])
def export_to_xl():
    # print('ok')
    # Define the path to your SQLite database
    db_path = 'daily_log.db'

    # Define the output file path with the current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'C:/Users/odaci/Downloads/dailyEffortLog/daily_log_export_{timestamp}.xlsx'

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Query the database to get all records from the daily_log table
    query = 'SELECT * FROM daily_log'
    df = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    # Write the DataFrame to an Excel file
    df.to_excel(output_file, index=False, engine='openpyxl')

    print(f"Data exported successfully to {output_file}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
