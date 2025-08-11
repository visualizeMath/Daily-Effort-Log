import sqlite3
from flask import Blueprint, render_template, request,flash,redirect,url_for
from  global_vars import db_path

submit_pdas_task_bp = Blueprint('submit_pdas_task_bp', __name__) 


@submit_pdas_task_bp.route('/submit_pdas_task', methods=['POST'])
def submit_pdas_task():
    pdas_task_id = request.form['pdas_task_id']
    pdas_task_aciklama = request.form['pdas_task_aciklama']
    bagli_sprint = request.form['bagli_sprint']

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute(f'select pdas_task_id from pdas where pdas_task_id ={pdas_task_id} and bagli_sprint={bagli_sprint}')
    sonuc=c.fetchone()
    
    print(f'Sonuc: {sonuc}')

    if not sonuc:
        c.execute('''INSERT INTO pdas (pdas_task_id, pdas_task_aciklama, bagli_sprint) 
                 VALUES (?, ?, ?)''', 
                 (pdas_task_id, pdas_task_aciklama, bagli_sprint))
        conn.commit()
        conn.close()
        flash(f'{pdas_task_id} - {pdas_task_aciklama} PDAS kaydı girildi.', 'success')
        
   
    elif sonuc and int(sonuc[0])> 0:
        flash(f'Aynı task numaralı başka bir kayıt var.', 'danger')
    
    return redirect(url_for('create_task_bp.create_new_task'))

