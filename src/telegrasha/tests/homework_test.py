
from handlers.homework import homework_set_ttt
from utils.subject import SUBJECTS_ENGNAME_DICT as SJDICT, Homework, SUBJECTS_FROM_ALIASES_DICT as SJ_AL_DICT
import datetime
import unittest

class TestHomeworkSetting(unittest.TestCase):
    text_vars = [
                'какое-то дз', 
                'приколы с упоминанием истории', 
                'что-то с первой группой да', 
                'и 2 группа, и русский язык афигеть'
                ]
    nongrooped_subject_vars = {k + 'дад' : v for k, v in SJ_AL_DICT if not v.is_grooped}
    sender = '_tester'
    bot_call_vars = ['Аркаша', 'аркаша', 'АРКАША', ]
    def test_simple_setting(self):
        for hw_text in self.text_vars:
            for sj_in_text, subject in self.nongrooped_subject_vars.items():


                self.assertEqual(homework_set_ttt(
                    'аркаша, по истории какое-то дз с упоминанием истории',
                    datetime.datetime(2023, 11, 7, 8, 8, 8),
                    self.sender
                ),
                (SJDICT['english'], 1, 45, 3, False, Homework(SJDICT['english'], 'какое-то дз с упоминанием истории', sender))
                )

