import sqlite3
from flask import Blueprint, render_template, request,flash,redirect,url_for
from  global_vars import db_path

submit_sprint_bp = Blueprint('submit_sprint_bp', __name__) 

@submit_sprint_bp.route('/submit_new_sprint', methods=['POST'])
def submit_new_sprint():
    sprintStart = request.form['sprintStart']
    sprintEnd = request.form['sprintEnd']
    sprintNo = request.form['sprintNo']
    isActive = request.form['isActive_Value']

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO sprints (sprint_no, sprint_start, sprint_end,is_Active) 
                 VALUES (?, ?, ?, ?)''', 
                 (   sprintNo, sprintStart, sprintEnd,isActive ))
    conn.commit()
    conn.close()

    if c.rowcount == 0:
        flash(f'Sprint kaydedilemedi.', 'danger')
    
    flash(f'Sprint {sprintNo} kaydı girildi.', 'success')

    return redirect(url_for('create_sprint_bp.create_new_sprint'))

