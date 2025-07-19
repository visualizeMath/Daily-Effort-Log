from datetime import datetime

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