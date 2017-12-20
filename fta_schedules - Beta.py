import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import datetime
import dateutil.parser



#Insert your FTA-Alias: e.g = myname7126
alias = ""

#Initialisations
get_session = requests.Session()


try:
    db_conn = sqlite3.connect('C:/Users/khz13/Desktop/Projects/db_FTA_Schedules.db', detect_types=sqlite3.PARSE_DECLTYPES)
    db_cursor = db_conn.cursor()
except sqlite3.Error as e:
    print(e)


#db Initialisation
with db_conn:
    try:
       db_cursor.execute('''CREATE TABLE IF NOT EXISTS FTA_Schedules(DATE TEXT NOT NULL,
                                                       CAPITAN TEXT NOT NULL,
                                                       CREW TEXT NOT NULL,
                                                       AIRCRAFT TEXT NOT NULL,
                                                       MODULE TEXT NOT NULL,
                                                       EXCERCISE TEXT NOT NULL,
                                                       DESCRIPTION TEXT NOT NULL,
                                                       FLY_TYPE TEXT NOT NULL);
                                                       ''')

       db_cursor.execute('''CREATE TABLE IF NOT EXISTS Last_Update (
       ID INT PRIMARY KEY NOT NULL,
       TIME_UTC timestamp NOT NULL,
       SUCCESSFUL INT NOT NULL);
       ''')
       print("DEBUG: SUCCESS - DBs Initialised")
    except sqlite3.Error as e:
        print(e)

def cls():
	os.system('CLS')
	return


def format_date(data, way):
    if way == "iso":
        date = datetime.datetime.strptime(data, "%d/%m/%y %H:%M").isoformat()
        return date 
    elif way == "display":
        date = datetime.datetime.strptime(data, "%Y-%m-%dT%H:%M:%S")
    return date


def update_schedules():
    if len(get_session.cookies) == 0:

        user_id = {'rdUsername': str(alias), 'rdFormLogon': 'True', 'rdPassword': str(alias), 'Submit1': 'Logon'}
        raw_schedule = get_session.post('http://202.158.223.244/OPS_STUDENT_REPORTS/rdPage.aspx', data = user_id)

        if raw_schedule.status_code == 200:
            print("DEBUG: GET - OK  |No Cookies \n")
        else:
            print("DEBUG: GET - ERROR: ", raw_schedule.status_code, " | No Cookies \n")

    elif len(get_session.cookies) == 1:
        raw_schedule = get_session.get('http://202.158.223.244/OPS_STUDENT_REPORTS/rdPage.aspx')
        if raw_schedule.status_code == 200:
            print("DEBUG: GET - OK |Cookies Sent \n")
        else:
           print("DEBUG: GET - ERROR: ", raw_schedule.status_code, " |Cookies Sent \n")

    return raw_schedule


def parse_data(data):

    day = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATUARDAY", "SUNDAY"]
    rem = ["Time", "Captain", "Crew", "Aircraft", "Module", "Exercise", "Description", "Fly Type"]
    in_vars = {"DATE": "", "CAPITAN": "", "CREW": "", "AIRCRAFT": "", "MODULE": "", "EXCERCISE": "", "DESCRIPTION": "", "FLY_TYPE": ""}
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

    #print("Row 1: ", row)
    #print("Row B: ", rowb)
    #print("Index: ", index)
    for a in index:
        date_time = rowb[a].split("-", 2)[1].replace(" ", "")
        date_time = date_time + " "+ rowb[a+1]
        in_vars["DATE"] = str(format_date(date_time, "iso"))

        if  ":" in rowb[(a+1)]:
            in_vars["CAPITAN"] = rowb[(a+2)]
            in_vars["CREW"] = rowb[(a+3)]
            in_vars["AIRCRAFT"] = rowb[(a+4)]
            in_vars["MODULE"] = rowb[(a+5)]
            in_vars["EXCERCISE"] = rowb[(a+6)]
            in_vars["DESCRIPTION"] = rowb[(a+7)]
            in_vars["FLY_TYPE"] = rowb[(a+8)]
        
        update_db(in_vars)
    return in_vars


def update_db(data):
    sqlquery = "SELECT * FROM FTA_Schedules WHERE"

    #Check if data is valid before comitting to db
    for k, v in data.items():
        if len(v) <1 or v == " ":
            print("Invalid Data for Flight: ", data["DATE"], "  -  ", data["DATE"], "\n", "- ", k, ": ", v,"\n", )
            break
    
    for key, value in data.items():
        if len(value)>0:
            sqlquery += " " + key + " = " + "'" + value +"' " + "AND "
    
    if sqlquery.rsplit(None, 1)[-1] == "AND":
        sqlquery = sqlquery.rsplit(None, 1)[0]
        with db_conn:
            try:
                retcurs = db_cursor.execute(sqlquery)
            except sqlite3.Error as e:
                print(e)
            
        rows = 0
        for row in retcurs:
            rows +=1
        if rows >=1:
            print("Flight Scheduled on: ", data["DATE"], "  -  Time: ", data["DATE"], "Already exist \n")
        else:
            with db_conn:
                try:
                    db_cursor.execute("INSERT INTO FTA_Schedules (DATE, CAPITAN, CREW, AIRCRAFT, MODULE, EXCERCISE, DESCRIPTION, FLY_TYPE) VALUES ('{}','{}', '{}', '{}','{}', '{}', '{}', '{}')".format(data["DATE"], data["CAPITAN"], data["CREW"], data["AIRCRAFT"], data["MODULE"], data["EXCERCISE"], data["DESCRIPTION"], data["FLY_TYPE"]))
                    db_conn.commit()
                except sqlite3.Error as e:
                    print(e)
        
        display()
    return data


def display():
    week_schedules = {}
    cls()
    with db_conn:
        try:
            items = db_cursor.execute("SELECT * FROM FTA_Schedules ORDER BY datetime(DATE) ASC")
        except sqlite3.OperationalError as e:
            print(e)
    for i in items:
        dt = format_date(i[0], "display")
        for k, v in week_schedules.items():
            if dt.strftime("%d/%M/Y%") == k:
                for key, value in v.items():
                    if dt.strftime("%H:%M") == key["time"]:
                        continue
            else:
                week_schedules[dt.strftime("%H:%M")] = {"TIME":"{}", "CAPITAN": "{}", "CREW": "{}", "AIRCRAFT": "{}", "MODULE": "{}", "EXCERCISE": "{}", "DESCRIPTION": "{}", "FLY_TYPE": "{}".format(dt.strftime("%H:%M"), i[1], i[2], i[3], i[4], i[5], i[6]. i[7] )}
                print(week_schedules, len(week_schedules))
    for k, v in week_schedules.items():
        print(110*"-")
        print(str(k)+ "\n")
        for key, value in v.items():
            print("--: ", str(k))

    
    return


if __name__ == "__main__":
    parse_data(update_schedules())
#Check both db and new_data if there was a change in flight time?
