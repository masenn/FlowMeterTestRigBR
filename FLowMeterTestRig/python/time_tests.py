from datetime import datetime, timezone
from zoneinfo import ZoneInfo

date = 1779933414
utc_time = datetime.fromtimestamp(date,tz=timezone.utc)
print(utc_time)