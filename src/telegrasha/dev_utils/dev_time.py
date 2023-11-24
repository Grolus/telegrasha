
import datetime
from utils.weekday import get_week_weekday_from_datetime


def dev_time_ttt(text: str, date: datetime.datetime):
    words = text.split(' ', 1)
    if len(words) > 1:
        try:
            new_date = datetime.datetime.fromisoformat(words[1])
        except ValueError:
            new_date = date
    else:
        new_date = date
    
    result = date, *get_week_weekday_from_datetime(date)
    return result
        

