from timeutils import isPast, canProcess, rateLimitCheck, getNow,getNowInSeconds
from dateutil.parser import parse


print(getNowInSeconds())

date1 = '2018-11-09T15:55:35-08:00'
date2 = '2018-11-09T15:58:35-08:00'

date4 = '2018-11-13T21:55:23Z'
date3 = '2018-11-13T21:45:23Z '
print(isPast(date1, 60*20))
print(canProcess(date1,date2))
 
print(canProcess(date3,date4))

dd = "2018-11-13T16:29:06.429143-08:00"
rateLimitCheck(dd, past=10)
print(parse(str(getNow())))