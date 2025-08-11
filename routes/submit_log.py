from flask import request,flash,jsonify,Blueprint,redirect,url_for
from global_vars import db_path
import sqlite3
from global_vars import get_tasks_for_sprint
from datetime import datetime

submit_log_bp = Blueprint('submit_log_bp', __name__) 

@submit_log_bp.route('/submit_log', methods=['POST'])
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