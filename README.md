# FTA_Schedules
A python script that checks/shows your weekly FTA flight schedules. 

Dependencies
- Requests
- BeautifulSoup
- sqlite3


This is still in development stage, not all features are implemented.

Please insert your FTA Alias into the "alias" variable the very top. 

# Screenshot
- Master Branch
![Screenshot1 tag](https://github.com/KHZ-INTL/FTA_Schedules/blob/master/flyfta.PNG)
- Beta Branch
    - Flights are displayed in dictionary form for time being until a display function is made or the db is integrated.
![Screenshot2 tag](https://github.com/KHZ-INTL/FTA_Schedules/blob/Beta/flyfta2.PNG)

Features- implemented:
 - Fetch and display client's schedules using FTA Alias on CLI
 - Base database structure for future imports of schedules
 - Get schedules with cookies, reduce cookie handling on server side.
 - Transfer data from html to Database

Features to implement:
 - Sort flights based on day, time, date
 - Check schedules automatically on set intervals (probably, every 30minutes), utilising last checked timestamp in db.
 - User Interface implementations: 
   - Notifications
   - Rain Meter UI plugin
 - If possible, Cortana implementation (voice commands):
    - Ask for next flight and associated flight details.
 
