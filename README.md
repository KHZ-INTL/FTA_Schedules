# FTA_Schedules
A python script that checks/shows your weekly FTA flight schedules. 

Dependencies
- Requests
- BeautifulSoup
- sqlite3
- texttable
- font awesome - optional


This is still in development stage, not all features are implemented.

Please assign your FTA Alias to the "alias" variable the very top of python file. 

# Screenshot
![Screenshot1 tag](https://github.com/KHZ-INTL/FTA_Schedules/blob/master/flyfta.png)

Features- implemented:
 - Fetch and display client's schedules using FTA Alias on CLI
 - Base database structure for future imports of schedules
 - Get schedules with cookies, reduce cookie handling on server side.

Features to implement:
 - Sort flights based on day, time, date
 - Check schedules automatically on set intervals (probably, every 30minutes), utilising last checked timestamp in db.
 - User Interface implementations: 
   - Notifications

 
