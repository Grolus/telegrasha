
import time


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
    """
    Принимает нынешние неделю и день недели и расчитывает, какой день недели из списка будет следующим после нынешнего
    Возвращает неделю и день недели
    """
    new_week, new_weekday = wd_up(now_weekday, dw, now_week)
    while new_weekday not in weekdays:
        new_week, new_weekday = wd_up(new_weekday, 1, new_week)
    return new_week, new_weekday

def get_now_week_weekday():
    t = time.gmtime(time.time())
    return t.tm_yday // 7 + 1, t.tm_wday

def find_numbers_in_text(text: str) -> list[int]:
    """Ищет числа в тексте и возвращает их список"""
    numbers = []
    current_number = ''
    saving = False
    for s in text:
        if s.isdigit() and saving:
            current_number += s
        elif s.isdigit():
            saving = True
            current_number += s
        else:
            saving = False
            if current_number:
                numbers.append(int(current_number))
            current_number = ''
    if current_number:
        numbers.append(int(current_number))
    return numbers

if __name__ == '__main__':
    text = 'paio f23 ca 41 asdjp c 3204582093 APOK 9 1231 AACL;K ;aKSD9 sad9f80a3'
    print(f'{text}: {find_numbers_in_text(text)}')
