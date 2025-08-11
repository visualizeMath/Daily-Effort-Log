from datetime import datetime
import sqlite3
from flask import Blueprint, request,flash,redirect,url_for
import pandas as pd
from  global_vars import db_path, get_downloads_folder

export_to_xl_bp = Blueprint('export_to_xl_bp', __name__) 

@export_to_xl_bp.route('/export_to_xl', methods=['GET','POST'])
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

