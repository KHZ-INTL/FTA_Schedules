# FTA_Schedules
A python script that checks/shows your weekly FTA flight schedules. 

Dependencies
- Requests
- BeautifulSoup
- sqlite3


This is still in development stage, not all features are implemented.

Features- implemented:
 - Fetch and display client's schedules using FTA Alias on CLI
 - Base database structure for future imports of schedules
 - Get schedules with cookies, reduce cookie handling on server side.

Features to implement:
 - Transfer data from html to Database
 - Sort flights based on day, time, date
 - Check schedules automatically on set intervals (probably, every 30minutes), utilising last checked timestamp in db.
 - User Interface implementations: 
   - Notifications
   - Rain Meter UI plugin
 - If possible, Cortana implementation (voice commands):
    - Ask for next flight and associated flight details.
 
