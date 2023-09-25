

def wd_up(wd: int, up: int, w: int | None=None): 
    wd += up
    while wd > 6:
        wd -= 7
        if w: w += 1
    if w: return w, wd
    return wd

def is_word_groop_name(word: str):
    return word in ('1', '2') or 'перв' in word or 'втор' in word

def word_to_group(word):
    if word == '1' or 'перв' in word: return 1
    if word == '2' or 'втор' in word: return 2
    return 0

def wd_calc(now_week: int, now_weekday:int, weekdays: list[int], dw: int=1):
    new_week, new_weekday = wd_up(now_weekday, dw, now_week)
    while new_weekday not in weekdays:
        new_week, new_weekday = wd_up(new_weekday, 1, new_week)
    return new_week, new_weekday
