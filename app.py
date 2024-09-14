from datetime import datetime
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for
import sqlite3
import secrets
import pandas as pd
import random

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
    
    c.execute('''CREATE TABLE IF NOT EXISTS dictionary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word_en TEXT,
                    word_tr TEXT,
                    word_de TEXT
                )''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    word2practice=getword2practice()
    # print('Cagrildi:'+str(word2practice[0][0]))
    # print('Cagrildi:'+str(word2practice[0][1]))
    return render_template('index.html',word2practice=word2practice)

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
    
    if c.rowcount == 0:
        flash(f'Kayıt oluşturulurken hata oluştu.', 'danger')
    flash(f'{formatted_tarih}- {gun} - {task_aciklama} icin efor kaydı girildi.', 'success')
    return redirect(url_for('index'))

def insert_vocab(file_path):
    conn=sqlite3.connect('daily_log.db')
    cursor=conn.cursor()
    print('insert_vocab called')

    with open(file_path, 'r', encoding='utf-8') as file:
        print('inside file reading')
        for line in file:
            word_en, word_tr = line.strip().split(';')
            cursor.execute('SELECT id FROM dictionary where word_en= ?',(word_en,))            
            row=cursor.fetchone()
            # print('Query returned: '+row)
            if row:
                print('Will be updated')
                #There's already a record for the word
                cursor.execute('UPDATE dictionary set word_tr= ? , word_de = ? where word_en= ?',(word_tr,None, word_en))
            else:
                print('Will be inserted')
                #The word doesn't exist. insert the word
                cursor.execute('INSERT INTO dictionary (word_en, word_tr, word_de) VALUES (?, ?, ?)', (word_en, word_tr, None))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Example usage:
# insert_words_from_file('path_to_your_file.txt')


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

    if c.rowcount == 0:
        flash(f'PDAS kaydı kaydedilemedi.', 'danger')
    flash(f'{pdas_task_id} - {pdas_task_aciklama} PDAS kaydı girildi.', 'success')

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
         
        flash(f'{task_id} numaralı PDAS taskı bulunamadi.', 'danger')
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
            flash(f'{task_id} numaralı PDAS taskı bulunamadi.', 'danger')
            return jsonify({"success": False, "error": "Task not found."}), 404

        flash(f'{task_id} numaralı PDAS taskı silindi.', 'success')
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
        flash(f'{task_id} numaralı efor kaydi bulunamadi.', 'danger')
        return jsonify({"success": False, "error": "Task ID not provided."}), 400
        # flash(f'ID bulunamadı: {str(e)}', 'danger')
    
    try:
        # Connect to the database and delete the task
        conn = sqlite3.connect('daily_log.db')
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

    if df.empty:
        print("No record found in the database..")
        flash(f'Veritabanında kayıt olmadığı için aktarım yapılmadı', 'warning')
        # return redirect(url_for('index'))
    else:
        print("There are records in the db..")

        # Close the database connection
        conn.close()

        # Write the DataFrame to an Excel file
        df.to_excel(output_file, index=False, engine='openpyxl')

        # print(f"Data exported successfully to {output_file}")
        flash(f'Dosya buraya kaydedildi: {output_file}', 'success')
    return redirect(url_for('index'))

def format_date(tarih):
    date_obj = datetime.strptime(tarih, '%d.%m.%Y')
    day = date_obj.strftime('%d')
    month_name = date_obj.strftime('%B')
    turkish_months = {
        'January': 'Ocak', 'February': 'Şubat', 'March': 'Mart', 
        'April': 'Nisan', 'May': 'Mayıs', 'June': 'Haziran', 
        'July': 'Temmuz', 'August': 'Ağustos', 'September': 'Eylül', 
        'October': 'Ekim', 'November': 'Kasım', 'December': 'Aralık'
    }
    return f"{day} {turkish_months[month_name]}"

# Route to generate the summary report
@app.route('/summary')
def summary():
    # Connect to the SQLite database
    conn = sqlite3.connect('daily_log.db')
    cursor = conn.cursor()

    # Fetch sum of harcanan_efor grouped by date (tarih)
    cursor.execute("""
        SELECT tarih, SUM(harcanan_efor) as total_efor 
        FROM daily_log 
        GROUP BY tarih
    """)
    rows = cursor.fetchall()
    
    # Filter only weekdays and format dates
    data = []
    for row in rows:
        # print(row)
        tarih, total_efor = row
        date_obj = datetime.strptime(tarih, '%d.%m.%Y')
        if date_obj.weekday() < 5:  # Weekdays only
            data.append({
                'tarih': format_date(tarih),
                'total_efor': total_efor,
                'color': get_color(total_efor)
            })
    
    conn.close()

    # Group into rows of 5 items per row
    # rows_of_circles = [data[i:i + 5] for i in range(0, len(data), 5)]
    rows_of_circles = []
    for i in range(0, len(data), 5):
        row_data = data[i:i + 5]
        row_total = sum(item['total_efor'] for item in row_data)
        rows_of_circles.append({'circles': row_data, 'row_total': row_total})

    word2practice=getword2practice()
    # print(str(word2practice))
    return render_template('summary.html', rows_of_circles=rows_of_circles,word2practice=word2practice)

# Determine the color of the circle based on total effort
def get_color(total_efor):
    if total_efor == 8:
        return 'green'
    elif total_efor > 0 and total_efor<8:
        return 'red'
    elif total_efor > 8:
        return 'orange'

def getword2practice():
    conn = sqlite3.connect('daily_log.db')
    cursor = conn.cursor()

    cursor.execute('SELECT count(*) from dictionary')
    word_count=cursor.fetchone()
    # print('WordCount: '+str(word_count))

    x=random.randint(1,word_count[0])
    cursor.execute(f'SELECT word_en,word_tr from dictionary where id={x}')
   
    selected_word=cursor.fetchall()
    conn.close()
    return selected_word
if __name__ == '__main__':
    # insert_vocab('templates/words.txt')
    app.run(debug=True)
    
