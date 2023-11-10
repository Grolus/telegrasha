import os
import json
import re
from typing import Sequence 
from config import HOMEWORK_STORAGE_PATH
from exceptions import HomeworkNotFoundError


class Subject():
    def __init__(self, name_ru: str, weekdays: list | tuple[list], aliases: list[str], name_eng: str):
        self.name_ru = name_ru
        self.name_eng = name_eng
        self.aliases = aliases
        self.weekdays = weekdays
        self.is_grouped = isinstance(weekdays, tuple)
    def __str__(self):
        return self.name_ru
    def load(self, week, weekday, group: int=''):
        try:
            with open(f'{HOMEWORK_STORAGE_PATH}{week}/{weekday}/{self.name_eng}{group if group else ""}.json', 'r') as file:
                loaded = json.load(file)
                return Homework(SUBJECTS_ENGNAME_DICT[loaded['subject_name']], loaded['text'], loaded['sender'], loaded['attachments'])
        except FileNotFoundError:
            raise HomeworkNotFoundError(self)


ALL_SUBJECTS = (
        Subject('Русский язык',     [1, 2, 3, 4],   ['рус'], 'russian'),
        Subject('Физика',           [0, 2, 4],      ['физик'], 'physics'),
        Subject('Литература',       [2, 4],         ['литре', 'литер'], 'literature'),
        Subject('Алгебра',          [0, 1, 2],      ['алгеб', 'матан', 'матем', 'матеш'], 'algebra'),
        Subject('Геометрия',        [3],            ['геом'], 'geometry'),
        Subject('Химия',            [1, 4],         ['хим'], 'chemistry'),
        Subject('Биология',         [2, 3],         ['биол'], 'biology'),
        Subject('История',          [0, 3],         ['истор'], 'history'),
        Subject('Обществознание',   [1],            ['обществ'], 'socienty'),
        Subject('Английский язык',  ([1, 2],[0, 1]),['англ', 'инглиш', 'ин яз', 'иняз'], 'english'),
        Subject('География',        [0, 4],         ['геогр'], 'geography'),
        Subject('ИКТ',              ([0], [2]),     ['икт', 'инф'], 'informatics'),
        Subject('Немецкий язык',    [0],            ['немец', 'немц'], 'german'),
        Subject('ОБЖ',              [4],            ['обж'], 'obzh'),
        Subject('Физкультура',      [2, 3],         ['физр', 'физкульт'], 'physculture'),
        Subject('Классный час',     [0],            ['кл час', 'классный час', 'класный час', 'классному часу', 'класному часу'], 'class_hour'),
        Subject('Технология',       [3],            ['техна', 'технологи', 'техне'], 'technology'),
        Subject('Индивидуальный проект', [4],       ['проект', 'проэкт'], 'projects'),
        #Subject('Отсутствие', [0], ['ничего', 'отсутств'], 'nothing')
    )

SUBJECTS_ENGNAME_DICT = {s.name_eng : s for s in ALL_SUBJECTS}
SUBJECTS_RUNAME_DICT = {s.name_ru : s for s in ALL_SUBJECTS}
GROOPED_SUBJECTS = [s for s in ALL_SUBJECTS if s.is_grouped]
ALL_SUBJECT_ALIASES = []
SUBJECTS_FROM_ALIASES_DICT = {}
for s in ALL_SUBJECTS:
    ALL_SUBJECT_ALIASES.extend(s.aliases)
    SUBJECTS_FROM_ALIASES_DICT.update({al : s for al in s.aliases})



def is_subject_in(text: str): 
    return any([i in text for i in ALL_SUBJECT_ALIASES])

def find_subject(text: str, default=None, return_end_pos: bool=False):
    """Find subject in `text`, if not found return `default`. 
    If `return_end_pos` set on `True`, returns position of last simbol of subject word
    """
    regex = '|'.join(ALL_SUBJECT_ALIASES)
    result = re.findall(regex, text)
    if not result:
        return default
    match_in_text = result[0]
    subject = SUBJECTS_FROM_ALIASES_DICT[match_in_text]
    if return_end_pos:
        end_pos = text.find(match_in_text) + len(match_in_text)
        while end_pos < len(text) and text[end_pos] != ' ':
            end_pos += 1
        return subject, end_pos - 1
    return subject
    




def _find_subject(text: str, default=None, return_end_pos: bool=False):
    """Outdated. Use `find_subject`"""
    subject = None
    for al in ALL_SUBJECT_ALIASES:
        if al in text:
            al_pos = text.find(al)
            dpos = 0
            for i in range(al_pos, len(text)):
                dpos += 1
                if text[i] == ' ': break
            end_pos = al_pos + dpos
            subject = SUBJECTS_FROM_ALIASES_DICT[al]
            break
    if subject:
        if return_end_pos:
            return subject, end_pos
        return subject
    return default



class Homework():
    def __init__(self, subject: Subject, text: str, sender: str, attachment: str='', is_empty: bool=None):
        self.subject = subject
        self.text = text
        self.sender = sender
        self.attachment = attachment
        self.is_attachment_multiple = ',' in self.attachment
        self.is_empty = is_empty if not (is_empty is None) else any((text, attachment))

    def save(self, week, weekday, group=''):
        if str(week) not in os.listdir(HOMEWORK_STORAGE_PATH):
            os.mkdir(f'{HOMEWORK_STORAGE_PATH}{week}')
        if str(weekday) not in os.listdir(f'{HOMEWORK_STORAGE_PATH}{week}'):
            os.mkdir(f'{HOMEWORK_STORAGE_PATH}{week}/{weekday}')
        with open(f'{HOMEWORK_STORAGE_PATH}{week}/{weekday}/{self.subject.name_eng}{group if group else ""}.json', 'w') as file:
            _dict = {'subject_name': self.subject.name_eng, 'text': self.text, 'sender': self.sender, 'attachments': self.attachment}
            json.dump(_dict, file)
        return True

    def to_line(self, number: int=None, group: int=None):
        return f'{"❌" if self.is_empty else "✅"}{f"{number}. " if number else ""}{self.subject}{f" {group} группа" if group else ""}' + \
            f'{f" (с вложением)" if self.attachment else ""}: {self.text if not self.is_empty else "неизвестно"}'

def hw_tuple_to_line(hw_tuple: Sequence[Homework], number: int=None) -> str:
    """Returns 2-lined homework line"""
    return '\n'.join([Homework.to_line(hw, number if not i else None, i+1) for i, hw in enumerate(hw_tuple)])

def _subject_identify(obj: Subject | str | Sequence) -> Subject | tuple[Subject]:
    if isinstance(obj, Subject):
        return obj
    elif subject := SUBJECTS_ENGNAME_DICT.get(obj):
        return subject
    elif subject := SUBJECTS_RUNAME_DICT.get(obj):
        return subject
    elif isinstance(obj, Sequence):
         return tuple(_subject_identify(s) for s in obj)
    raise ValueError(f'All of subjects must me Subject instance or valid subject name (error: {obj})')

def subject_to_hw_send_line(subject: Subject, week: int, weekday: int, group: int=0):
    raw_line = f'{subject.name_ru}{f" [{group}] группа" if group else ""}'
    if hw := subject.load(week, weekday, str(group) if group else ''):
        line = f'✅{raw_line}{f" (c вложением🧩)" if hw.attachment else ""}: {hw.text}'
    else:
        line = f'❌{raw_line} не найдено'
    return line


class Timetable():
    def __init__(self, weekday: int, *subjects: Subject | str):
        self.weekday = weekday
        self.subjects = []
        for s in subjects:
            self.subjects.append(_subject_identify(s))
        #print(f'Registered timetable:\n    {", ".join([s.name_ru if isinstance(s, Subject) else f"{s[0].name_ru}/{s[1].name_ru}" for s in self.subjects])}')

ALL_TIMETABLES = (
    Timetable(0, 'Классный час', 'География', 'История', 'Немецкий язык', 'Алгебра', 'Физика', ('ИКТ', 'Английский язык')),
    Timetable(1, 'algebra', ('english', 'english'), 'chemistry', 'socienty', 'russian', 'algebra'),
    Timetable(2, 'biology', 'algebra', 'physics', 'russian', 'physculture', 'literature', ('english', 'informatics')),
    Timetable(3, 'biology', 'history', 'geometry', 'technology', 'geometry', 'physculture', 'russian'),
    Timetable(4, 'geography', 'projects', 'obzh', 'chemistry', 'russian', 'literature', 'physics')
)



