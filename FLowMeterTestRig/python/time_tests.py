from datetime import datetime, timezone
from zoneinfo import ZoneInfo

date_1 = 1780302248
utc_time_1 = datetime.fromtimestamp(date_1,tz=timezone.utc)
date_2 = 1780302250
utc_time_2 = datetime.fromtimestamp(date_2,tz=timezone.utc)



print(utc_time_2.second-utc_time_1.second)