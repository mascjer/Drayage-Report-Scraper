# Drayage Report Scraper

An application for Port Services employees to use this web app and the excel sheet they store container information on to scrape the GCT Terminal website instead of manually entering information from the website.

## Access and Features

[App can be accessed at this address](http://lin2dv2ap209:3000/). Reach out to MASCJER for any questions or concerns.

The app contains the below functionality:
  1) User uploads drayage report excel file
  2) Web app logs into GCT Terminal website and begins looking for visibile containers
    - Containers that show data when searched in container history
  4) Web app stores dates for available_date, full_out_date, empty_in_date, Transload Recieved, OTW ERA
  5) Web app determines new Status 
    - Returned, Empty in Yard, Full in Yard, At Port, On the Water
  6) Web app then displays new data in a data table that can be downloaded by the user
