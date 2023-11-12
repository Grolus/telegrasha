
from handlers.homework import homework_set_ttt, full_homework_request_ttt
from utils.subject import (
    SUBJECTS_ENGNAME_DICT as SJDICT, 
    SUBJECTS_FROM_ALIASES_DICT as SJ_AL_DICT, ALL_TIMETABLES,
    Homework, 
    Subject,
    compare_homework_lists
    )
import datetime
import unittest

class TestHomeworkSetting(unittest.TestCase):
    text_vars = [
                'какое-то дз', 
                'приколы с упоминанием истории', 
                'что-то с первой группой да', 
                'и 2 группа, и русский язык афигеть'
                ]
    nongrooped_subject_vars = {k + 'дад' : v for k, v in SJ_AL_DICT.items() if not v.is_grouped}
    sender = '_tester'
    bot_call_vars = ['Аркаша, ', 'аркаша ', 'АРКАША, ', '']
    pre_sj_words = ['по', 'задание по', 'дз по']
    def test_simple_setting(self):
        for hw_text in self.text_vars:
            for sj_in_text, subject in self.nongrooped_subject_vars.items():
                for call in self.bot_call_vars:
                    for pre_sj in self.pre_sj_words:
                        compiled_req = f'{call}{pre_sj} {sj_in_text} {hw_text}'
                        self.assertEqual(first := homework_set_ttt(
                            compiled_req,
                            datetime.datetime(2023, 11, 5, 8, 8, 8),
                            self.sender
                        )[-1],
                        second := Homework(subject, hw_text, self.sender),
                        msg=f'{str(first)}; {str(second)}'
                        )


class TestHomeworkRequest(unittest.TestCase):
    ...

class TestFullHomeworkRequest(unittest.TestCase):
    wd_word_vars = {1: 'завтра', 0: 'сегодня', 0: 'понед', 0: 'понедельник', 1: 'вторник', 2: 'среду', 3: 'четверг', 4: 'пятниц'}
    def test_request(self):
        for wd, wd_word in self.wd_word_vars.items():
            req = f'что задали на {wd_word}'
            first = full_homework_request_ttt(
                    req,
                    datetime.datetime(2023, 11, 6, 8, 8, 8)
            )[-1]
            second = [Homework(s) if isinstance(s, Subject) 
                         else (Homework(s[0]), Homework(s[1])) 
                         for s in ALL_TIMETABLES[wd].subjects]
            self.assertTrue(
            compare_homework_lists(first, second),
            '\n'.join(map(str, first)) + '\n\n' + '\n'.join(map(str, second))
            )


