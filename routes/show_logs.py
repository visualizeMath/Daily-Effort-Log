import sqlite3
from flask import Blueprint, render_template, request 
import global_vars

show_logs_bp = Blueprint('show_logs_bp', __name__) 


@show_logs_bp.route('/show_logs',methods=['GET','POST'])
def show_logs():

    selected_month=global_vars.get_current_month_name()
    conn = sqlite3.connect(global_vars.db_path)
    c = conn.cursor()

    if request.method=='GET':
        month_no = global_vars.get_current_month()
        c.execute('SELECT * FROM daily_log WHERE tarih like ? ORDER BY id DESC', ('%.{}.%'.format(month_no),))

        # c.execute('SELECT * FROM daily_log ORDER BY id DESC')

    if request.method=='POST':

        selected_month= request.form.get('filter_month')

        if (selected_month!='' and selected_month and selected_month!='Select'):
            
            month_number =global_vars.turkish_month_map.get(selected_month)
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
