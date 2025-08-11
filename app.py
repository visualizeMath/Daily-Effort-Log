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
from routes.activate_sprint import activate_sprint_bp
from routes.submit_log import submit_log_bp
from routes.submit_task import submit_pdas_task_bp
from routes.summary import summary_bp
from routes.update_task import update_effort_explanation_bp
from routes.get_day_effort import get_day_effort_bp
from routes.export2excel import export_to_xl_bp
from routes.get_task_name import get_selectedtaskname_bp
from routes.export import export_bp

from global_vars import turkish_month_map
from global_vars import turkish_number2month
from global_vars import get_current_month_name
from global_vars import get_current_month
from global_vars import get_current_year
from global_vars import get_tasks_for_sprint
from global_vars import get_taskname_for_selected_task
from global_vars import insert_vocab
from global_vars import getword2practice


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
app.register_blueprint(activate_sprint_bp)
app.register_blueprint(submit_log_bp)
app.register_blueprint(submit_pdas_task_bp)
app.register_blueprint(summary_bp)
app.register_blueprint(update_effort_explanation_bp)
app.register_blueprint(get_day_effort_bp)
app.register_blueprint(export_to_xl_bp)
app.register_blueprint(get_selectedtaskname_bp)
app.register_blueprint(export_bp)

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
    
    return render_template('index.html',word2practice=word2practice)
    
if __name__ == '__main__':
    # insert_vocab('templates/words.txt')
    app.run(debug=True)
    
