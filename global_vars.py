from datetime import datetime
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