import os
import json


HW_STORAGE_PATH = 'data/homework/'


class Subject():
    def __init__(self, name_ru: str, weekdays: list | tuple[list], aliases: list[str], name_eng: str):
        self.name_ru = name_ru
        self.name_eng = name_eng
        self.aliases = aliases
        self.weekdays = weekdays
        self.is_grouped = isinstance(weekdays, tuple)
    def load(self, week, weekday, group=''):
        try:
            with open(f'{HW_STORAGE_PATH}{week}/{weekday}/{self.name_eng}{group if group else ""}.json', 'r') as file:
                loaded = json.load(file)
                return Homework(SUBJECTS_ENGNAME_DICT[loaded['subject_name']], loaded['text'], loaded['sender'], loaded['attachments'])
        except:
            return False

class Homework():
    def __init__(self, subject: Subject, text: str, sender: str, attachment: str=''):
        self.subject = subject
        self.text = text
        self.sender = sender
        self.attachment = attachment
        
    def save(self, week, weekday, group=''):
        if str(week) not in os.listdir(HW_STORAGE_PATH):
            os.mkdir(f'{HW_STORAGE_PATH}{week}')
        if str(weekday) not in os.listdir(f'{HW_STORAGE_PATH}{week}'):
            os.mkdir(f'{HW_STORAGE_PATH}{week}/{weekday}')
        with open(f'{HW_STORAGE_PATH}{week}/{weekday}/{self.subject.name_eng}{group if group else ""}.json', 'w') as file:
            _dict = {'subject_name': self.subject.name_eng, 'text': self.text, 'sender': self.sender, 'attachments': self.attachment}
            json.dump(_dict, file)
        return True

    



ALL_SUBJECTS = (
        Subject('Русский язык', [1, 2, 3, 4], ['рус'], 'russian'),
        Subject('Физика', [0, 2, 4], ['физик'], 'physics'),
        Subject('Литература', [2, 4], ['литре', 'литер'], 'literature'),
        Subject('Алгебра', [0, 1, 2], ['алгеб', 'матан', 'матем', 'матеш'], 'algebra'),
        Subject('Геометрия', [3], ['геом'], 'geometry'),
        Subject('Химия', [1, 4], ['хим'], 'chemistry'),
        Subject('Биология', [2, 3], ['биол'], 'biology'),
        Subject('История', [0, 3], ['истор'], 'history'),
        Subject('Обществознание', [1], ['обществ'], 'socienty'),
        Subject('Английский язык', ([1, 2], [0, 1]), ['англ', 'инглиш', 'ин яз', 'иняз'], 'english'),
        Subject('География', [0, 4], ['геогр'], 'geography'),
        Subject('ИКТ', ([0], [2]), ['икт', 'инф'], 'informatics'),
        Subject('Немецкий язык', [0], ['немец', 'немц'], 'german'),
        Subject('ОБЖ', [4], ['обж'], 'obzh'),
        Subject('Физкультура', [2, 3], ['физр', 'физкульт'], 'physculture'),
        Subject('Классный час', [0], ['кл час', 'классный час', 'класный час'], 'class_hour'),
        Subject('Технология', [3], ['техна', 'технологи', 'техне'], 'technology'),
        Subject('Индивидуальный проект', [4], ['проект', 'проэкт'], 'projects'),
        #Subject('Отсутствие', [0], ['ничего', 'отсутств'], 'nothing')
    )

SUBJECTS_ENGNAME_DICT = {s.name_eng : s for s in ALL_SUBJECTS}
GROOPED_SUBJECTS = [s for s in ALL_SUBJECTS if s.is_grouped]
