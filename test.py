from datetime import datetime


avail = '9/23/22 6:04:18 PM'
print(avail)

date_time_obj = datetime.strptime(avail, '%m/%d/%y %I:%M:%S %p')

print(date_time_obj)

only_in_24_hour_format = datetime.strftime(date_time_obj, "%H:%M")
print(only_in_24_hour_format)