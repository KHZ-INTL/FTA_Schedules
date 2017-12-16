import requests
from bs4 import BeautifulSoup
import sqlite3






#Insert your FTA-Alias:
alias = ""

#Initialisations
get_session = requests.Session()




try:
    db_conn = sqlite3.connect('db_FTA_Schedules.db')
    db_cursor = db_conn.cursor()
except sqlite3.Error as e:
    print(str(e), "Applciation db is missing?")


#db Initialisation
with db_conn:
    try:
        db_cursor.execute('''CREATE TABLE FTA_Schedules
                        (ID INT PRIMARY KEY NOT NULL,
                        DATE DATE NOT NULL,
                        DAY TEXT NOT NULL,
                        PLANTIME TEXT NOT NULL,
                        CAPITAN TEXT NOT NULL,
                        CREW TEXT NOT NULL,
                        AIRCRAFT TEXT NOT NULL,
                        MODULE TEXT NOT NULL,
                        EXCERCISE TEXT NOT NULL,
                        DESCRIPTION TEXT NOT NULL,
                        FLY_TYPE TEXT NOT NULL
                        );''')
        db_cursor.execute('''CREATE TABLE Last_Update
                        (ID INT PRIMARY KEY NOT NULL,
                        TIME_UTC timestamp NOT NULL,
                        SUCCESSFUL INT NOT NULL);
                        ''')
        print("DEBUG: SUCCESS - Created Tables")
    except sqlite3.Error as e:
        print(e)



def update_schedules():
    if len(get_session.cookies) == 0:
        # Session Initialisation
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
    soup = BeautifulSoup(data.text, 'html.parser')
    table = soup.find("table")
    table_rows = table.find_all("tr")
    for tr in table_rows:
        td = tr.find_all("td")
        row = [i.text for i in td]
        print(row)
    return row 
#Parse Schedules

if __name__ == "__main__":
    raw_schedule = update_schedules()
    parse_data(raw_schedule)
   
    
    
# table = soup.find("table")
# table_rows = table.find_all("tr")
# for tr in table_rows:
# td = tr.find_all('td')
# row = [i.text for i in td]
# print(row)

#This returns html unparsed:
#row = []
#for i in td:
#   if i:
#       row.append(i)
    
