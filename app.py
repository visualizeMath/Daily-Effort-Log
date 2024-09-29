from datetime import datetime
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for
import sqlite3
import secrets
import pandas as pd
import random
import os
from pathlib import Path

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
  
    active_sprints=get_sprints_with_active_tasks()
    # print(type(active_sprints))
    # print(active_sprints[0])
    return render_template('enter_log.html', task_ids=[],active_sprints=active_sprints)
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
    c.execute(f'SELECT pdas_task_id,pdas_task_aciklama FROM pdas WHERE bagli_sprint ={sprint_no} ')
   
    dependent_tasks=[]

    for row in c.fetchall():
        # print('satir: '+row[0]+' \n')
        spNo=row[0].strip()
        task_description=row[1].strip()
        # print(task_description)

        if(len(spNo)>0 and spNo.isdigit()):
            dependent_tasks.append(spNo+';'+task_description)
        
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


@app.route('/show_logs',methods=['GET','POST'])
def show_logs():

    selected_month=get_current_month_name()
    conn = sqlite3.connect('daily_log.db')
    c = conn.cursor()

    if request.method=='GET':
        c.execute('SELECT * FROM daily_log ORDER BY id DESC')

    elif request.method=='POST':

        selected_month= request.form.get('filter_month')

        if (selected_month!='' and selected_month and selected_month!='Select'):
            
            month_number = turkish_month_map.get(selected_month)
            # print('2.month_number : '+ month_number)
            # query = "SELECT * FROM daily_log WHERE Tarih LIKE ? Order by id desc"
            # c.execute(query, ('%.{}.%'.format(month_value),))
            query = "SELECT * FROM daily_log WHERE tarih like ? ORDER BY id DESC"
            c.execute(query, ('%.{}.%'.format(month_number),))

        elif selected_month=='Select' :
            c.execute('SELECT * FROM daily_log ORDER BY id DESC')

    logs = c.fetchall()
    # c.execute('SELECT * FROM daily_log order by tarih desc')
  
    conn.close()
    return render_template('show_logs.html', logs=logs,selected_month=selected_month)

turkish_month_map = {
    "Ocak": "01",
    "Şubat": "02",
    "Mart": "03",
    "Nisan": "04",
    "Mayıs": "05",
    "Haziran": "06",
    "Temmuz": "07",
    "Ağustos": "08",
    "Eylül": "09",
    "Ekim": "10",
    "Kasım": "11",
    "Aralık": "12"
}

turkish_number2month = {
    "01":"Ocak",
    "02":"Şubat",
    "03":"Mart",
    "04":"Nisan",
    "05":"Mayıs",
    "06":"Haziran",
    "07":"Temmuz",
    "08":"Ağustos",
    "09":"Eylül",
    "10":"Ekim",
    "11":"Kasım", 
    "12":"Aralık"
}

def get_current_month_name():
   dtn=datetime.now()
   cm=dtn.strftime("%m")

#    print(cm)
#    print(turkish_number2month.get(cm))
   return turkish_number2month.get(cm)

@app.route('/show_pdas_items')
def show_pdas_items():
    conn = sqlite3.connect('daily_log.db')
    c = conn.cursor()
    c.execute('SELECT * FROM pdas order by id desc')
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

#Find the downloads folder path depending on the os of the user
# This path will be used to export the records
def get_downloads_folder():
    if os.name == 'nt':  # Windows
        return Path(os.getenv('USERPROFILE')) / 'Downloads'
    else:  # macOS and Linux
        return Path.home() / 'Downloads'
    
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

@app.route('/export',methods=['GET'])
def export():
    return render_template('export.html')

@app.route('/export_to_xl', methods=['GET','POST'])
def export_to_xl():
    db_path = 'daily_log.db'

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    downloads_folder=get_downloads_folder()

    output_file = f'{downloads_folder}/daily_log_export_{timestamp}.xlsx'

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    query = 'SELECT * FROM daily_log order by tarih'
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

def get_current_month():
    dtn=datetime.now()
    cm=dtn.strftime("%m")
    return cm

def get_current_year():
    dtn=datetime.now()
    cy=dtn.strftime("%Y")
    return cy

# Route to generate the summary report
@app.route('/summary')
def summary():
    print('Summary route called')
    # Connect to the SQLite database
    conn = sqlite3.connect('daily_log.db')
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

    # print(rows)
    related_efforts_of_day=[]
    # Filter only weekdays and format dates
    data = []
    for row in rows:
        # print(row)
        tarih, total_efor = row
        get_tasks_of_day(tarih)
        date_obj = datetime.strptime(tarih, '%d.%m.%Y')
        if date_obj.weekday() < 5:  # Weekdays only
            data.append({
                'tarih': format_date(tarih),
                'total_efor': total_efor,
                'color': get_color(total_efor),
                'related_efforts': get_tasks_of_day(tarih)
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

def get_tasks_of_day(given_date):
    conn=sqlite3.connect('daily_log.db')
    cursor=conn.cursor()
    # print(given_date)
    cursor.execute("select * from daily_log where tarih = ?",(given_date,))
    tasks_of_day= cursor.fetchall()

    # for task in tasks_of_day:
    #     print(f'{task[0]}{task[1]}{task[2]}')

    conn.close()

    return tasks_of_day

def getword2practice():
    conn = sqlite3.connect('daily_log.db')
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

def get_sprints_with_active_tasks():
    conn= sqlite3.connect('daily_log.db')
    cursor =conn.cursor()

    cursor.execute('select max( distinct bagli_sprint) from pdas')
    available_sprints= cursor.fetchall()
    conn.close()

    return available_sprints

if __name__ == '__main__':
    # insert_vocab('templates/words.txt')
    app.run(debug=True)
    
