
from datetime import datetime
from typing import Sequence
from utils.subject import (
    find_subject,
    ALL_SUBJECT_ALIASES,
    SUBJECTS_FROM_ALIASES_DICT,
    GROOPED_SUBJECTS,
    ALL_TIMETABLES,
    Homework,
    Subject
)
from utils.weekday import (
    get_week_weekday_from_datetime as get_wwd,
    wd_calc,
    wd_in_text_master
)
from utils.tools import photos_to_str, find_group_in_text
from utils.constants import WEEKDAYS_CALLS, OLD_HOMEWORK_WORDS
from exceptions import (HomeworkSettingError, EmptyHomeworkError, GroupNotFoundError,
                        HomeworkNotFoundError, WeekWeekdayNotFoundError, OldHomeworkNotFoundError)

def homework_set_ttt(text: str, 
                     date: datetime, 
                     sender: str, 
                     attachment: list=None
                     ) -> tuple[Subject, int, int, int, bool, Homework]:
    """Saves homework parsed from `text` and `attachment` if exists. 
    If succesful, returns information about saved homework in format:
    (`subject`, `group`, `new_week`, `new_weekday`, `is_for_next_week`, `collected_homework`)"""
    text_orig = text
    text = text_orig.lower()
    
    # subject searching
    subject, info_end_pos = find_subject(text, return_end_pos=True)

    # group searchig
    group = 0
    if subject in GROOPED_SUBJECTS:
        group, info_end_pos = find_group_in_text(text, True)
        if group == 0:
            raise GroupNotFoundError(subject)
        
    # time compile
    now_week, now_weekday = get_wwd(date)
    finded = False
    if ' на ' in text:
        for i, call in enumerate(WEEKDAYS_CALLS):
            if call in text:
                weekday = i
                new_week, new_weekday = wd_calc(now_week, now_weekday, [weekday])
                finded = True
                break
    if not finded:
        new_week, new_weekday = wd_calc(now_week, now_weekday, subject.weekdays[group-1] if subject.is_grouped else subject.weekdays)
    print(f'({now_week}, {now_weekday}) -> ({new_week}, {new_weekday})')
    is_for_next_week = new_week > now_week

    # text compile
    hw_text = text_orig[info_end_pos:].strip()


    # attachment saving
    
    attachment_str = photos_to_str(attachment)

    # homework saving
    collected_homework = Homework(subject, hw_text, sender, attachment_str)
    for old_word in OLD_HOMEWORK_WORDS:
        if hw_text == old_word:
            old_week, old_weekday = wd_calc(now_week, now_weekday, subject.weekdays, -1, 0)
            try:
                collected_homework = subject.load(old_week, old_weekday, group)
            except HomeworkNotFoundError:
                raise OldHomeworkNotFoundError(subject, old_weekday, old_week < now_week, group)


    if not collected_homework.text and not collected_homework.attachment:
        raise EmptyHomeworkError(subject)
    collected_homework.save(new_week, new_weekday, group)
    return (subject, group, new_week, new_weekday, is_for_next_week, collected_homework)

def homework_request_ttt(
        text: str,
        date: datetime
        ) -> tuple[Homework, int, int, int, bool]:
    """
    Loads and returns loaded homework for `text`. \n
    Raises `HomeworkNotFoundError` if homework was not saved or 
    `GroupNotFoundError` if group is invalid.\n
    On succes returns:
    tuple(`loaded_homework`, `group`, `new_week`, `new_weekday`, `is_for_next_week`)
    """
    text = text.lower()
    text_words = text.split()

    # subject searching
    for al in ALL_SUBJECT_ALIASES:
        if al in text:
            subject: Subject = SUBJECTS_FROM_ALIASES_DICT[al]
            break
    
    # group searching
    group = 0
    if subject in GROOPED_SUBJECTS:
        group = find_group_in_text(text)
        if group == 0:
            raise GroupNotFoundError(subject)

    # time compile
    now_week, now_weekday = get_wwd(date)
    new_week, new_weekday = wd_calc(now_week, now_weekday, 
                                    subject.weekdays[group - 1] if subject.is_grouped else subject.weekdays)
    is_for_next_week = new_week > now_week

    # homework loading
    if not (loaded_homework := subject.load(new_week, new_weekday, group)):
        raise HomeworkNotFoundError(subject, group)
    return (loaded_homework, group, new_week, new_weekday, is_for_next_week)

def full_homework_request_ttt(text: str, date: datetime) -> tuple[int, int, bool, list[Homework | list[Homework]]]:
    """
    Loads homework for entire day parsed from `text`. \n
    On succes returns tuple: (`week`, `weekday`, `is_for_next_week`, `homeworks`)
    """
    text = text.lower()

    # time compile
    now_week, now_weekday = get_wwd(date)
    if not (wwd := wd_in_text_master(now_week, now_weekday, text)):
        raise WeekWeekdayNotFoundError()
    week, weekday = wwd
    is_for_next_week = week > now_week

    # answer compile
    subjects_to_load_hw = ALL_TIMETABLES[weekday].subjects
    homeworks = []
    for sj in subjects_to_load_hw:
        if isinstance(sj, Sequence):
            homeworks.append([])
            for i in range(2):
                try:
                    hw = sj[i].load(week, weekday, i + 1)
                except HomeworkNotFoundError:
                    hw = Homework(sj[i], is_empty=True)
                homeworks[-1].append(hw)
        else:
            try:
                homeworks.append(sj.load(week, weekday))
            except HomeworkNotFoundError:
                homeworks.append(Homework(sj, is_empty=True))

    return (week, weekday, is_for_next_week, homeworks)

