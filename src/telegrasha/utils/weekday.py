"""Utils for working with weeks and weekdays"""
import time
import datetime
from .constants import WEEKDAYS_CALLS, IS_ON_SERVER

def wd_up(weekday: int, d: int, week: int=None):
    """Изменяет день недели `weekday` на число `d`. Изменяет неделю `week`, если она задана"""
    weekday += d
    while weekday > 6:
        weekday -= 7
        if week: 
            week += 1
    while weekday < 0:
        weekday += 7
        if week:
            week -= 1
    if week: 
        return week, weekday
    return weekday

def wd_calc(now_week: int, now_weekday:int, weekdays: list[int], step: int=1, needed_change: int=1):
    """
    Принимает нынешние неделю и день недели и расчитывает, какой день недели из списка будет следующим после нынешнего
    Возвращает неделю и день недели
    """
    new_week, new_weekday = wd_up(now_weekday, needed_change, now_week)
    while new_weekday not in weekdays:
        new_week, new_weekday = wd_up(new_weekday, step, new_week)
    return new_week, new_weekday

def get_now_week_weekday():
    t = time.gmtime(time.time())
    return t.tm_yday // 7 + 1, t.tm_wday

def get_week_weekday_from_datetime(dt: datetime.datetime):
    tm_time = time.gmtime(dt.timestamp() + 21600)
    w, wd = tm_time.tm_yday // 7 + 1, tm_time.tm_wday
    if wd > 4: w -= 1
    if wd == 5 and IS_ON_SERVER: w += 1 
    return w, wd

def wd_in_text_master(
        now_week: int,
        now_weekday: int,
        text: str 
        ) -> tuple[int, int] | None:
    weekday = None
    for i, call in enumerate(WEEKDAYS_CALLS):
        if call in text:
            weekday = i
            break
    if weekday is None:
        if 'сегодня' in text:
            weekday = now_weekday
        elif 'завтра' in text:
            weekday = wd_up(now_weekday, 1)
        else:
            return None
    week = now_week + 1 if now_weekday > weekday else now_week
    return week, weekday


