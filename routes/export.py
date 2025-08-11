from flask import render_template,Blueprint
from global_vars import db_path

export_bp = Blueprint('export_bp', __name__) 

@export_bp.route('/export',methods=['GET'])
def export():
    return render_template('export.html')
