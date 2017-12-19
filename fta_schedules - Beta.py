import requests
from bs4 import BeautifulSoup
import sqlite3


#Insert your FTA-Alias: e.g = myname7126
alias = ""

#Initialisations
get_session = requests.Session()


try:
    db_conn = sqlite3.connect('db_FTA_Schedules.db')
    db_cursor = db_conn.cursor()
except sqlite3.Error as e:
    print(e)


#db Initialisation
#with db_conn:
#    try:
#       db_cursor.execute('''CREATE TABLE FTA_Schedules(DATE Text NOT NULL,
#                                                      DAY TEXT NOT NULL,
#                                                       PLANTIME TEXT NOT NULL,
#                                                       CAPITAN TEXT NOT NULL,
#                                                       CREW TEXT NOT NULL,
#                                                       AIRCRAFT TEXT NOT NULL,
#                                                       MODULE TEXT NOT NULL,
#                                                       EXCERCISE TEXT NOT NULL,
#                                                     DESCRIPTION TEXT NOT NULL,
#                                                       FLY_TYPE TEXT NOT NULL);
 #                                                      ''')
 #
  #      db_cursor.execute('''CREATE TABLE Last_Update (
   #                                             ID INT PRIMARY KEY NOT NULL,
    #                                            TIME_UTC timestamp NOT NULL,
     #                                           SUCCESSFUL INT NOT NULL);''')
      #  print("DEBUG: SUCCESS - Created Tables")
    #except sqlite3.Error as e:
     #   print(e)


def update_schedules():
    if len(get_session.cookies) == 0:

        user_id = {'rdUsername': str(alias), 'rdFormLogon': 'True', 'rdPassword': str(alias), 'Submit1': 'Logon'}
        raw_schedule = get_session.post('http://202.158.223.244/OPS_STUDENT_REPORTS/rdPage.aspx', data = user_id)

        if raw_schedule.status_code == 200:
            print("DEBUG: GET - OK  |No Cookies")
        else:
            print("DEBUG: GET - ERROR: ", raw_schedule.status_code, " | No Cookies")

    elif len(get_session.cookies) == 1:
        raw_schedule = get_session.get('http://202.158.223.244/OPS_STUDENT_REPORTS/rdPage.aspx')
        if raw_schedule.status_code == 200:
            print("DEBUG: GET - OK |Cookies Sent")
        else:
            print("DEBUG: GET - ERROR: ", raw_schedule.status_code, " |Cookies Sent")

    return raw_schedule


def parse_data(data):

    day = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATUARDAY", "SUNDAY"]
    rem = ["Time", "Captain", "Crew", "Aircraft", "Module", "Exercise", "Description", "Fly Type"]
    in_vars = {"date": "", "day": "", "ptime": "", "cpt": "", "crew": "", "ac": "", "mod": "", "ex": "", "desc": "", "type": ""}
    row = []
    rowb = []
    index = []

    soup = BeautifulSoup(data.text, 'html.parser')
    table = soup.find("table")
    table_rows = table.find_all("tr")

    for tr in table_rows:
        td = tr.find_all('td')
        [row.append(i.text) for i in td]
    
    for i in row:
        if i in rem or i == "":
            continue
        else:
            rowb.append(i)
    
    for i in rowb:
        for d in day:
            if d in str(i):
                index.append((rowb.index(i)))

    for a in index:
        date_day = rowb[a].split("-", 2)
        in_vars["day"] = str(date_day[0].replace(" ", ""))
        in_vars["date"] = str(date_day[1].replace(" ", ""))
        print(rowb[a+1])
        if  ":" in rowb[(a+1)]:
            in_vars["ptime"] = rowb[(a+1)]
            in_vars["cpt"] = rowb[(a+2)]
            in_vars["crew"] = rowb[(a+3)]
            in_vars["ac"] = rowb[(a+4)]
            in_vars["mod"] = rowb[(a+5)]
            in_vars["ex"] = rowb[(a+6)]
            in_vars["desc"] = rowb[(a+7)]
            in_vars["type"] = rowb[(a+8)]
        print(in_vars)


    return in_vars


def to_db(data):
    

    with db_conn:
        try:
            db_cursor.execute("INSERT INTO FTA_Schedules (DATE, DAY, PLANTIME, CAPITAN, CREW, AIRCRAFT, MODULE, EXCERCISE, DESCRIPTION, FLY_TYPE) VALUES ('{}', '{}', '{}','{}', '{}', '{}','{}', '{}', '{}', '{}')".format(in_vars["date"], in_vars["day"], in_vars["ptime"], in_vars["cpt"], in_vars["crew"], in_vars["ac"], in_vars["mod"], in_vars["ex"], in_vars["desc"], in_vars["type"]))
            db_conn.commit()
        except sqlite3.Error as e:
            print(e)

    return data



if __name__ == "__main__":
    parse_data(update_schedules())
    
