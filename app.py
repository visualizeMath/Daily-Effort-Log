from collections import OrderedDict
from datetime import datetime
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for
import sqlite3
import secrets
import pandas as pd
import random
import os
from pathlib import Path
from routes.delete_sprint import delete_sprint_bp
from routes.create_sprint import create_sprint_bp
from routes.create_task import create_task_bp
from routes.show_tasks import show_tasks_bp
from routes.show_sprints import show_sprints_bp
from routes.show_logs import show_logs_bp
from routes.submit_sprint import submit_sprint_bp
from routes.delete_task import delete_task_bp
from routes.get_dependent_tasks import get_dependent_task_bp
from routes.delete_log import delete_log_bp
from routes.enter_log import enter_log_bp

from global_vars import turkish_month_map
from global_vars import turkish_number2month
from global_vars import get_current_month_name
from global_vars import get_current_month
from global_vars import get_current_year
from global_vars import get_tasks_for_sprint
from global_vars import get_taskname_for_selected_task

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

# Registering the blueprint with main Flask app
app.register_blueprint(delete_sprint_bp)
app.register_blueprint(create_sprint_bp)
app.register_blueprint(create_task_bp)
app.register_blueprint(show_tasks_bp)
app.register_blueprint(show_sprints_bp)
app.register_blueprint(show_logs_bp)
app.register_blueprint(submit_sprint_bp)
app.register_blueprint(delete_task_bp)
app.register_blueprint(get_dependent_task_bp)
app.register_blueprint(delete_log_bp)
app.register_blueprint(enter_log_bp)

db_path = 'daily_log.db'

def init_db():
    conn = sqlite3.connect(db_path)
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
    
    c.execute('''CREATE TABLE IF NOT EXISTS sprints (
                    sprint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sprint_no TEXT,
                    sprint_start TEXT,
                    sprint_end TEXT,
                    is_Active TEXT
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

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO daily_log (task_id, task_aciklama, tarih,gun, harcanan_efor, yapilan_is) 
                 VALUES (?, ?, ?, ?, ?, ?)''', 
                 (task_id, task_aciklama, formatted_tarih,gun, harcanan_efor, yapilan_is))
    conn.commit()
    conn.close()
    
    if c.rowcount == 0:
        flash(f'Kayıt oluşturulurken hata oluştu.', 'danger')
    flash(f'{formatted_tarih}- {gun} - {task_aciklama} icin efor kaydı girildi.', 'success')
    return redirect(url_for('enter_log_bp.enter_log'))

def insert_vocab(file_path):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

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

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO pdas (pdas_task_id, pdas_task_aciklama, bagli_sprint) 
                 VALUES (?, ?, ?)''', 
                 (pdas_task_id, pdas_task_aciklama, bagli_sprint))
    conn.commit()
    conn.close()

    if c.rowcount == 0:
        flash(f'PDAS kaydı kaydedilemedi.', 'danger')
    flash(f'{pdas_task_id} - {pdas_task_aciklama} PDAS kaydı girildi.', 'success')

    return redirect(url_for('create_task_bp.create_new_task'))


#Find the downloads folder path depending on the os of the user
# This path will be used to export the records
def get_downloads_folder():
    if os.name == 'nt':  # Windows
        return Path(os.getenv('USERPROFILE')) / 'Downloads'
    else:  # macOS and Linux
        return Path.home() / 'Downloads'
    


@app.route('/export',methods=['GET'])
def export():
    return render_template('export.html')

@app.route('/export_to_xl', methods=['GET','POST'])
def export_to_xl():
    db_path = 'daily_log.db'

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    downloads_folder=get_downloads_folder()
    # downloads_folder='/app/data/'

    output_file = f'{downloads_folder}/daily_log_export_{timestamp}.xlsx'

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    query = 'SELECT * FROM daily_log order by tarih'
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("No record found in the database..")
        flash(f'Veritabanında kayıt olmadığı için aktarım yapılmadı', 'warning')
        # return redirect(url_for('index'))
    else:
        print("There are records in the db..")

        # Close the database connection
        # conn.close()

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
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    current_year = get_current_year().strip()
    current_month = get_current_month().strip()

    # print('Current Year: '+current_year)
    # print('Current Month: '+current_month)

    # Fetch sum of harcanan_efor grouped by date (tarih)
    cursor.execute("""
        SELECT tarih, SUM(harcanan_efor) as total_efor 
        FROM daily_log 
        WHERE tarih LIKE ?
        GROUP BY tarih
    """,(f'%.{current_month}.{current_year}',))
    rows = cursor.fetchall()
    
    # print(f"Pattern used: %.{current_month}.{current_year}")
    # print("Fetched rows:", rows)

    # print(rows)
    related_efforts_of_day=[]
    # Filter only weekdays and format dates
    data = []
    for row in rows:
        # print(row)
        tarih, total_efor = row
        get_tasks_of_day(tarih)
        date_obj = datetime.strptime(tarih, '%d.%m.%Y')
        # if date_obj.weekday() < 5:  # Weekdays only
        data.append({
            'tarih': format_date(tarih),
            'total_efor': total_efor,
            'date_obj':date_obj,
            'week': date_obj.isocalendar()[1],
            'color': get_color(total_efor),
            'related_efforts': get_tasks_of_day(tarih)
        })
    
    conn.close()
    # group by week number in order
    weeks = OrderedDict()
    for item in sorted(data, key=lambda x: x['date_obj']):
        weeks.setdefault(item['week'], []).append(item)

    # build rows_of_weeks
    rows_of_weeks = []
    for week_no, items in weeks.items():
        row_total = sum(i['total_efor'] for i in items)
        rows_of_weeks.append({
            'week_no': week_no,
            'circles': items,
            'row_total': row_total
        })

    return render_template(
        'summary.html',
        rows_of_weeks=rows_of_weeks,
        turkish_month_name=get_current_month_name()
    )
'''
    # Group into rows of 5 items per row
    # rows_of_circles = [data[i:i + 5] for i in range(0, len(data), 5)]
    rows_of_circles = []
    for i in range(0, len(data), 5):
        row_data = data[i:i + 5]
        row_total = sum(item['total_efor'] for item in row_data)
        rows_of_circles.append({'circles': row_data, 'row_total': row_total})

    # word2practice=getword2practice()
    turkish_month_name=get_current_month_name()

    return render_template('summary.html', rows_of_circles=rows_of_circles,turkish_month_name=turkish_month_name)
'''

# Determine the color of the circle based on total effort
def get_color(total_efor):
    if total_efor == 8:
        return 'green'
    elif total_efor > 0 and total_efor<8:
        return 'red'
    elif total_efor > 8:
        return 'orange'
 

def get_tasks_of_day(given_date):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    # print(given_date)
    cursor.execute("select * from daily_log where tarih = ?",(given_date,))
    tasks_of_day= cursor.fetchall()

    # for task in tasks_of_day:
    #     print(f'{task[0]}{task[1]}{task[2]}')

    conn.close()

    return tasks_of_day

def getword2practice():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT count(*) from dictionary')
    word_count=cursor.fetchone()
    # print('WordCount: '+str(word_count))
    if word_count[0]>0:
        x=random.randint(1,word_count[0])
        cursor.execute(f'SELECT word_en,word_tr from dictionary where id={x}')
    
        selected_word=cursor.fetchall()
        conn.close()
        return selected_word
    else:
        conn.close()
        return None


@app.route('/update_effort_explanation', methods=['POST'])
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


if __name__ == '__main__':
    # insert_vocab('templates/words.txt')
    app.run(debug=True)
    
