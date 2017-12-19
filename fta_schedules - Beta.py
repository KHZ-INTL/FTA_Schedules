import requests
from bs4 import BeautifulSoup
import sqlite3
import os

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
with db_conn:
    try:
       db_cursor.execute('''CREATE TABLE IF NOT EXISTS FTA_Schedules(DATE Text NOT NULL,
                                                      DAY TEXT NOT NULL,
                                                       PLANTIME TEXT NOT NULL,
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
    in_vars = {"DATE": "", "DAY": "", "PLANTIME": "", "CAPITAN": "", "CREW": "", "AIRCRAFT": "", "MODULE": "", "EXCERCISE": "", "DESCRIPTION": "", "FLY_TYPE": ""}
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
        date_day = rowb[a].split("-", 2)
        in_vars["DAY"] = str(date_day[0].replace(" ", ""))
        in_vars["DATE"] = str(date_day[1].replace(" ", ""))

        if  ":" in rowb[(a+1)]:
            in_vars["PLANTIME"] = rowb[(a+1)]
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
            print("Invalid Data for Flight: ", data["DATE"], "  -  ", data["PLANTIME"], "\n", "- ", k, ": ", v,"\n", )
            break
    
    for key, value in data.items():
        if len(value)>0:
            sqlquery += " " + key + " = " + "'" + value +"' " + "AND "
    
    if sqlquery.rsplit(None, 1)[-1] == "AND":
        sqlquery = sqlquery.rsplit(None, 1)[0]
        with db_conn:
            retcurs = db_cursor.execute(sqlquery)
        rows = 0
        for row in retcurs:
            rows +=1
        if rows >=1:
            print("Flight Scheduled on: ", data["DATE"], "  -  Time: ", data["PLANTIME"], "Already exist \n")
        else:
            with db_conn:
                try:
                    db_cursor.execute("INSERT INTO FTA_Schedules (DATE, DAY, PLANTIME, CAPITAN, CREW, AIRCRAFT, MODULE, EXCERCISE, DESCRIPTION, FLY_TYPE) VALUES ('{}', '{}', '{}','{}', '{}', '{}','{}', '{}', '{}', '{}')".format(data["DATE"], data["DAY"], data["PLANTIME"], data["CAPITAN"], data["CREW"], data["AIRCRAFT"], data["MODULE"], data["EXCERCISE"], data["DESCRIPTION"], data["FLY_TYPE"]))
                    db_conn.commit()
                except sqlite3.Error as e:
                    print(e)
        
        display()
    return data


def display():
	cls()
	with db_conn:
		try:
			items = db_cursor.execute("SELECT * FROM FTA_Schedules")
			for i in items:
				print(110*"-")
				print("| ", i,  15*" ", "|")
				print(110*"-")
				print("\n")
		except sqlite3.OperationalError as e:
			print(e)
	return "a"


if __name__ == "__main__":
    parse_data(update_schedules())
#Check both db and new_data if there was a change in flight time?
