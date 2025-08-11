from collections import OrderedDict
from flask import request,flash,jsonify,Blueprint,redirect,url_for,render_template
from global_vars import db_path, format_date, get_color, get_current_month_name, get_tasks_of_day
import sqlite3
from datetime import datetime
from global_vars import get_current_month
from global_vars import get_current_year


summary_bp = Blueprint('summary_bp', __name__) 

# Route to generate the summary report
@summary_bp.route('/summary')
def summary():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
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


    # print(f"Pattern used: %.{current_month}.{current_year}")
    # print("Fetched rows:", rows)

    # print(rows)
    related_efforts_of_day=[]
    # Filter only weekdays and format dates
    data = []
    for row in rows:
        # print(row)
        tarih, total_efor = row
        get_tasks_of_day(tarih)
        date_obj = datetime.strptime(tarih, '%d.%m.%Y')
        # if date_obj.weekday() < 5:  # Weekdays only
        data.append({
            'tarih': format_date(tarih),
            'total_efor': total_efor,
            'date_obj':date_obj,
            'week': date_obj.isocalendar()[1],
            'color': get_color(total_efor),
            'related_efforts': get_tasks_of_day(tarih)
        })
    
    conn.close()
    # group by week number in order
    weeks = OrderedDict()
    for item in sorted(data, key=lambda x: x['date_obj']):
        weeks.setdefault(item['week'], []).append(item)

    # build rows_of_weeks
    rows_of_weeks = []
    for week_no, items in weeks.items():
        row_total = sum(i['total_efor'] for i in items)
        rows_of_weeks.append({
            'week_no': week_no,
            'circles': items,
            'row_total': row_total
        })

    return render_template(
        'summary.html',
        rows_of_weeks=rows_of_weeks,
        turkish_month_name=get_current_month_name()
    )