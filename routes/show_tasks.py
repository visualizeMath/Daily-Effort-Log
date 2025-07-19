import sqlite3
from flask import Blueprint, render_template,request
import global_vars

show_tasks_bp = Blueprint('show_tasks_bp', __name__) 

@show_tasks_bp.route('/show_tasks',methods=['GET','POST'])
def show_tasks():
    conn = sqlite3.connect(global_vars.db_path)
    c = conn.cursor()

    c.execute('SELECT max(sprint_no) son_sprint from sprints')
    max_sprint=c.fetchone()

    if max_sprint is not None and max_sprint[0]:
        # print(f'max_sprint:{max_sprint[0]}')
        selected_sprint=max_sprint[0]

    if request.method=='POST':
        # print(f'Method: {request.method}')
        selected_sprint= request.form.get('filter_sprint')
        
        print(f'selected_sprint:{selected_sprint}')

        if selected_sprint == "Select":
            selected_sprint = 'All'

        if (selected_sprint!='' and selected_sprint and selected_sprint!='All'):

            query = "SELECT * FROM pdas WHERE bagli_sprint = ? ORDER BY id DESC"
            c.execute(query, (selected_sprint,))

        elif selected_sprint=='All' :
            c.execute('SELECT * FROM pdas ORDER BY id DESC')
        
        tasks = c.fetchall()
        conn.close()

        return render_template('show_tasks.html', tasks=tasks,selected_sprint=selected_sprint,max_sprint=int(max_sprint[0]))
    else:
        # print(f'selected ilk : {selected_sprint}')
         qs = request.args.get("filter_sprint")
         
         if qs and qs != "All":
            selected_sprint = qs
         else:
            selected_sprint = max_sprint[0]

        # if (selected_sprint=='' or selected_sprint=='All' ) and max_sprint is not None and max_sprint[0]:
        #     selected_sprint=max_sprint[0]
        
         query = "SELECT * FROM pdas WHERE bagli_sprint = ? ORDER BY id DESC"
         c.execute(query, (selected_sprint,))
        
         tasks = c.fetchall()
    
         conn.close()
         return render_template('show_tasks.html', tasks=tasks,selected_sprint=selected_sprint,max_sprint=int(max_sprint[0]))
    
    # c.execute('SELECT * FROM pdas order by id desc')
    # pdas_logs = c.fetchall()

    # conn.close()
    # return render_template('show_tasks.html', logs=pdas_logs,max_sprint=max_sprint)
