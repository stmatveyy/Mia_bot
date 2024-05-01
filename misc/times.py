from datetime import datetime as dt
from datetime import time, timedelta

TODAY_EVN = dt.combine(dt.now().date(), time(17,0))

TOMORROW_MOR = dt.combine(dt.now().date() + timedelta(days=1), time(9,0))

DAYS_3 = dt.combine(dt.now().date() + timedelta(days=3), time(9,0))

WEEKENDS = dt.combine(dt.now().date() + timedelta(5 - dt.now().weekday()), time(12,0))
