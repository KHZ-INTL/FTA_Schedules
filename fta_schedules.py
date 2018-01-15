#!/bin/python3

"""FTA Schedules
View your FTA Flight Schedules/sorties
"""

import datetime
import os
import sqlite3

import requests
from bs4 import BeautifulSoup
from texttable import Texttable

# Insert your FTA-Alias: e.g = myname7226
alias = "anvari7126"

# Initialisations
get_session = requests.Session()


try:
    db_conn = sqlite3.connect(
        'FTA_Schedules.db',
        detect_types=sqlite3.PARSE_DECLTYPES)
    db_cursor = db_conn.cursor()
except sqlite3.Error as e:
    print(e)


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
    except sqlite3.Error as e:
        print(e)


def cls():
    """Clear Screen
    This function Clears the screen
    """

    os.system('CLEAR')
    return


def format_date(data, method):
    """Format date/time string to and from iso standard
    This function is mainly used to format date before inserting into to the data base
    Arguments:
        data {string} -- [date/time string]
        method {string} -- [the value of string is used to decide wether convert data (date/time string) into iso or %d/%m/%YT:%H:%M:%S]
    Returns:
        date -- dateTime object
    """
    if method == "iso":
        date = datetime.datetime.strptime(data, "%d/%m/%y %H:%M").isoformat()
        return date
    elif method == "display":
        date = datetime.datetime.strptime(data, "%Y-%m-%dT%H:%M:%S")
    return date


def request_data():
    """Get raw data from FTA online schedules portal website using Requests utilising cookies
    Alias variable is used as login credential when requesting student schedules
    Returns:
        raw_schedule -- return html data from the get request
    """
    if len(get_session.cookies) == 0:

        user_id = {
            'rdUsername': str(alias),
            'rdFormLogon': 'True',
            'rdPassword': str(alias),
            'Submit1': 'Logon'}
        raw_schedule = get_session.post(
            'http://202.158.223.244/OPS_STUDENT_REPORTS/rdPage.aspx', data=user_id)

        if raw_schedule.status_code == 200:
            print("DEBUG: GET - OK  |No Cookies \n")
        else:
            print(
                "DEBUG: GET - ERROR: ",
                raw_schedule.status_code,
                " | No Cookies \n")

    elif len(get_session.cookies) == 1 or len(get_session.cookies) > 1:
        raw_schedule = get_session.get(
            'http://202.158.223.244/OPS_STUDENT_REPORTS/rdPage.aspx')
        if raw_schedule.status_code == 200:
            print("DEBUG: GET - OK |Cookies Sent \n")
        else:
            print(
                "DEBUG: GET - ERROR: ",
                raw_schedule.status_code,
                " |Cookies Sent \n")

    return raw_schedule


def parse_data(data):

    """Parse raw html data (data) using BeautifulSoup into a dictionary

    Arguments:
        data {html} -- the result of GET request for student schedules

    Returns:
        in_vars -- dictionary which contains schedule information
        
    """

    day = [
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATUARDAY",
        "SUNDAY"]
    rem = [
        "Time",
        "Captain",
        "Crew",
        "Aircraft",
        "Module",
        "Exercise",
        "Description",
        "Fly Type"]
    in_vars = {
        "DATE": "",
        "CAPITAN": "",
        "CREW": "",
        "AIRCRAFT": "",
        "MODULE": "",
        "EXCERCISE": "",
        "DESCRIPTION": "",
        "FLY_TYPE": ""}
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
        date_time = rowb[a].split("-", 2)[1].replace(" ", "")
        date_time = date_time + " " + rowb[a + 1]
        in_vars["DATE"] = str(format_date(date_time, "iso"))

        if ":" in rowb[(a + 1)]:
            in_vars["CAPITAN"] = rowb[(a + 2)]
            in_vars["CREW"] = rowb[(a + 3)]
            in_vars["AIRCRAFT"] = rowb[(a + 4)]
            in_vars["MODULE"] = rowb[(a + 5)]
            in_vars["EXCERCISE"] = rowb[(a + 6)]
            in_vars["DESCRIPTION"] = rowb[(a + 7)]
            in_vars["FLY_TYPE"] = rowb[(a + 8)]

        update_db(in_vars)
    return in_vars


def update_db(data):
    """Insert schedules extracted and parsed into data base 
    Arguments:
        data {Dictionary} -- Contains Parsed schedule information
    Returns:
        None -- Returns Nothing
    """
    sqlquery = "SELECT * FROM FTA_Schedules WHERE"

    # Check if data is valid before comitting to db
    for k, v in data.items():
        if len(v) < 1 or v == " ":
            print(
                "Invalid Data for Flight: ",
                data["DATE"],
                "  -  ",
                data["DATE"],
                "\n",
                "- ",
                k,
                ": ",
                v,
                "\n",
            )
            break

    for key, value in data.items():
        if len(value) > 0:
            sqlquery += " " + key + " = " + "'" + value + "' " + "AND "

    if sqlquery.rsplit(None, 1)[-1] == "AND":
        sqlquery = sqlquery.rsplit(None, 1)[0]
        with db_conn:
            try:
                retcurs = db_cursor.execute(sqlquery)
            except sqlite3.Error as e:
                print(e)

        rows = 0
        for row in retcurs:
            rows += 1
        if rows >= 1:
            print(
                "Flight Scheduled on: ",
                data["DATE"],
                "  -  Time: ",
                data["DATE"],
                "Already exist \n")
        else:
            with db_conn:
                try:
                    db_cursor.execute(
                        "INSERT INTO FTA_Schedules (DATE, CAPITAN, CREW, AIRCRAFT, MODULE, EXCERCISE, DESCRIPTION, FLY_TYPE) VALUES ('{}','{}', '{}', '{}','{}', '{}', '{}', '{}')".format(
                            data["DATE"],
                            data["CAPITAN"],
                            data["CREW"],
                            data["AIRCRAFT"],
                            data["MODULE"],
                            data["EXCERCISE"],
                            data["DESCRIPTION"],
                            data["FLY_TYPE"]))
                    db_conn.commit()
                except sqlite3.Error as e:
                    print(e)

        db_get_schedules()
    return None


def db_get_schedules():

    """Extracts schedules from sqlite data base and sort by day before displaying and returning as dictionary
    Generates a dictionary with kies being as dates of each flight schedules and values as time of flight with its detail
    Returns:
        Dictionary -- Flight schedules dictionary sorted for flights in each day
    """
    week_schedules = {}
    latest = {}
    existing = {}
    cls()
    with db_conn:
        try:
            items = db_cursor.execute(
                "SELECT * FROM FTA_Schedules ORDER BY datetime(DATE) ASC")
        except sqlite3.OperationalError as e:
            print(e)
    for i in items:
        dt = format_date(i[0], "display")
        dt_date = dt.strftime("%d/%m/%Y")
        dt_time = dt.strftime("%H:%M:%S")
        dt_hr = dt.strftime("%H:%M")
        if dt_date in week_schedules.keys():
            if dt_hr in week_schedules[dt_date]:
                print(
                    "Sorty on: ",
                    dt_date,
                    " ",
                    dt_time,
                    " was changed/updated: ")
                continue
            elif dt_hr not in week_schedules[dt_date]:
                latest[dt_hr] = {
                    "TIME": dt_hr,
                    "CAPITAN": i[1],
                    "CREW": i[2],
                    "AIRCRAFT": i[3],
                    "MODULE": i[4],
                    "EXCERCISE": i[5],
                    "DESCRIPTION": i[6],
                    "FLY_TYPE": i[7]}
                existing = {}
                for kies, values in week_schedules[dt_date].items():
                    existing[kies] = values

                existing.update(latest)
                week_schedules[dt_date] = existing

        elif dt_date not in week_schedules.keys():
            week_schedules[dt_date] = {
                dt_hr: {
                    "TIME": dt_hr,
                    "CAPITAN": i[1],
                    "CREW": i[2],
                    "AIRCRAFT": i[3],
                    "MODULE": i[4],
                    "EXCERCISE": i[5],
                    "DESCRIPTION": i[6],
                    "FLY_TYPE": i[7]}}
    cli_display(week_schedules)

    return week_schedules


def order_schedules(schedules):
    pass


def cli_display(schedules):
    """Print schedules in a pretty table

    Arguments:
        schedules {Dictionary} -- Flight Schedules sorted per day

    Returns:
        type] -- description
    """
    space = [" ", " ", " ", " ", " ", " ", " ", " ", " "]
    table = Texttable()
    table.set_cols_align(["c", "c", "c", "c", "c", "c", "c", "c", "c"])
    table.set_cols_valign(["m", "m", "m", "m", "m", "m", "m", "m", "m"])
    table.set_cols_width([10, 10, 10, 10, 10, 10, 13, 15, 15])
    table.header([" DATE",
                  " TIME",
                  " CAPITAN",
                  " CREW",
                  " AIRCRAFT",
                  " MODULE",
                  " EXCERCISE",
                  " DESCRIPTION",
                  " FLY-TYPE"])

    for key, value in schedules.items():
        if len(schedules[key].keys()) > 1:
            ret = []
            for ke, val in schedules[key].items():
                if "/" in str(key):
                    ret.append(str(key))
                else:
                    ret.append(" ")
                for key, value in val.items():
                    ret.append(value)
                table.add_row(ret)
                ret = []
        elif len(schedules[key].keys()) == 1:
            ret = []
            ret.append(str(key))
            for key, value in schedules[key].items():
                for ke, val in value.items():
                    ret.append(val)
            table.add_row(ret)
            table.add_row(space)
    print(table.draw(), "\n")

    return schedules


if __name__ == "__main__":
    parse_data(request_data())
