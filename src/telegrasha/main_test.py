
from handlers.homework import homework_request_ttt, full_homework_request_ttt
from datetime import datetime
from utils.weekday import get_week_weekday_from_datetime
import time

for mday in [23, 24, 25, 26, 27]:
    print(mday)
    dt = datetime(2024, 2, mday)
    print(get_week_weekday_from_datetime(dt))
    print(time.gmtime(dt.timestamp()))

