from datetime import datetime
import os
from pathlib import Path
import random
import sqlite3

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


db_path = 'daily_log.db'


def get_current_month_name():
   dtn=datetime.now()
   cm=dtn.strftime("%m")

   return turkish_number2month.get(cm)


def get_current_month():
    dtn=datetime.now()
    cm=dtn.strftime("%m")
    return cm

def get_current_year():
    dtn=datetime.now()
    cy=dtn.strftime("%Y")
    return cy


def get_tasks_for_sprint(sprint_no):
    conn = sqlite3.connect(db_path)
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
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f'SELECT pdas_task_aciklama FROM pdas WHERE pdas_task_id ={task_id} ')
   
    task_name=''

    for row in c.fetchall():
        current_task_name=row[0].strip()
        if(len(current_task_name)>0):
            task_name=current_task_name
    conn.close()    
    return task_name

def get_sprints_with_active_tasks():
    conn= sqlite3.connect(db_path)
    cursor =conn.cursor()


    # cursor.execute(10 max( bagli_sprint) from pdas where pdas_task_id BETWEEN 4114 and 5000')
    cursor.execute('select max(sprint_no) from sprints where is_Active="Yes"')
    
    available_sprints= cursor.fetchall()
    conn.close()

    return available_sprints


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

# Determine the color of the circle based on total effort
def get_color(total_efor):
    if total_efor == 8:
        return 'green'
    elif total_efor > 0 and total_efor<8:
        return 'red'
    elif total_efor > 8:
        return 'orange'

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
    
def calculate_total_effort(selected_date):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%d.%m.%Y')
    print(formatted_date)
    c.execute(f"SELECT  SUM(harcanan_efor) as total_efor FROM daily_log WHERE tarih ='{formatted_date}' ")
   
    total_effort=c.fetchone() 
    
    conn.close()  

    return total_effort


#Find the downloads folder path depending on the os of the user
# This path will be used to export the records
def get_downloads_folder():
    if os.name == 'nt':  # Windows
        return Path(os.getenv('USERPROFILE')) / 'Downloads'
    else:  # macOS and Linux
        return Path.home() / 'Downloads'