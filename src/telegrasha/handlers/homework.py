
from datetime import datetime
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
from utils.tools import word_to_group, photos_to_str
from utils.constants import WEEKDAYS_CALLS
from exceptions import (HomeworkSettingError, EmptyHomeworkError, GroupNotFoundError,
                        HomeworkNotFoundError, WeekWeekdayNotFoundError)

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
    text_words = text.split()
    
    # subject searching
    subject, info_end_pos = find_subject(text, return_end_pos=True)

    # group searchig
    group = 0
    if subject in GROOPED_SUBJECTS:
        tmp_text = text[info_end_pos:].strip() # текст начиная с конца названия предмета (без пробелов в начале и конце)
        tmp_text_words = tmp_text.split()
        if 'груп' in tmp_text_words[1]:
            if group := word_to_group(tmp_text_words[0]):
                weekdays_key = group - 1
                info_end_pos = text.find(tmp_text_words[1]) + len(tmp_text_words[1])
                pass
        if not group:
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
        new_week, new_weekday = wd_calc(now_week, now_weekday, subject.weekdays[weekdays_key] if subject.is_grouped else subject.weekdays)
        print(f'({now_week}, {now_weekday}) -> ({new_week}, {new_weekday})')
    is_for_next_week = new_week > now_week

    # text compile
    hw_text = text_orig[info_end_pos:]

    # attachment saving
    attachment_str = photos_to_str(attachment)

    # homework saving
    collected_homework = Homework(subject, hw_text, sender, attachment_str)
    if not collected_homework.text and not collected_homework.attachment:
        raise EmptyHomeworkError(subject)
    if not collected_homework.save(new_week, new_weekday, group):
        raise HomeworkSettingError(subject)
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
    is_grooped_in_msg = len(text_words) > 3 and word_to_group(text_words[3])
    # subject searching
    for al in ALL_SUBJECT_ALIASES:
        if al in text:
            subject: Subject = SUBJECTS_FROM_ALIASES_DICT[al]
            break
    
    # group searching
    weekdays_key = None
    group = 0
    if subject in GROOPED_SUBJECTS:
        if is_grooped_in_msg:
            if group := word_to_group(text_words[3]):
                weekdays_key = group - 1
        if weekdays_key is None:
            raise GroupNotFoundError(subject)

    # time compile
    now_week, now_weekday = get_wwd(date)
    new_week, new_weekday = wd_calc(now_week, now_weekday, subject.weekdays[weekdays_key] if subject.is_grouped else subject.weekdays)
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
        sj: Subject
        if sj in GROOPED_SUBJECTS:
            homeworks.append([])
            for i in range(1,3):
                try:
                    hw = sj.load(week, weekday, i)
                except HomeworkNotFoundError:
                    hw = None
                homeworks[-1].append(hw)
        else:
            try:
                homeworks.append(sj.load(week, weekday))
            except HomeworkNotFoundError:
                homeworks.append(Homework(sj, '', '', is_empty=True))

    return (week, weekday, is_for_next_week, homeworks)

