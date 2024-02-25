
from utils.constants import WEEKDAYS_GENITIVE
import handlers

class Error(BaseException):
    def __init__(self) -> None:
        pass
    msg_text = 'ошибка ~~'
    pass
class HomeworkError(Error):
    pass
class RequestError(Error):
    """Error in user request"""
    pass
class SubjectRequestError(RequestError):
    def __init__(self, subject=None):
        """Error in request associated with subject"""
        self.subject = subject
class HomeworkSettingError(SubjectRequestError):
    """Error in homework setting"""
    @property
    def msg_text(self):
        return f'Не удалось сохранить дз по {self.subject.name_ru}'
    pass
class EmptyHomeworkError(HomeworkSettingError):
    @property
    def msg_text(self):
        return f'Не сохранил пустое дз по {self.subject.name_ru}'
    pass
class HomeworkRequestError(SubjectRequestError):
    pass
class GroupNotFoundError(HomeworkSettingError, HomeworkRequestError):
    @property
    def msg_text(self):
        return f'''Не понял, какая группа предмета {self.subject} вам нужна.
Первая группа - те, кто у Власовой; Вторая - те, кто у Рыбкиной. 
Повторите (или измените исходное) сообщение по шаблону: 
по [предмет] [номер группы] группа ...''' 
class HomeworkNotFoundError(HomeworkError, HomeworkRequestError):
    def __init__(self, subject, group: int=0):
        super().__init__(subject)
        self.group = group
    @property
    def msg_text(self):
        return f'Не найдено задания по {self.subject}{f" ({self.group} группа)" if self.group else ""}.'
class OldHomeworkNotFoundError(HomeworkNotFoundError):
    def __init__(self, subject, old_weekday: int, is_for_last_week: bool=False, group: int = 0):
        super().__init__(subject, group)
        self.old_weekday = old_weekday
        self.is_for_last_week = is_for_last_week
    @property
    def msg_text(self):
        return f'Не найдено старого задания по {self.subject}{f" ({self.group} группа)" if self.group else ""}.' + \
            f' Искал его на {WEEKDAYS_GENITIVE[self.old_weekday]} {"прошлой" if self.is_for_last_week else "этой"} недели. ' + \
            f'Сохраните его вручную, пожалуйста.'
class WeekWeekdayNotFoundError(RequestError):
    msg_text = 'Не понял, на какой день нужно задание.'
class InvalidWeekday(RequestError):
    msg_text = f"Напишите подходящий день недели."
class AnecdoteError(Error):
    pass
class NoAnecdotesError(AnecdoteError):
    msg_text = 'К сожалению, у меня нет анекдотов :( Но ты можешь его записать! ' + \
               'Просто напиши "Анекдот: [сам анекдот]" или ответьте на сообщение с анекдотом сообщением "анекдот"'
class AnecdoteRequestError(RequestError, AnecdoteError):
    msg_text = f'''Если вы пытались сохранить анекдот, то что то пошло не так. 
Ответьте на сообщение с анекдотом сообщением "Анекдот" или напишите его сами: 
"Анекдот: [текст анекдота]"'''
class AnecdoteNotFoundError(AnecdoteRequestError):
    def __init__(self, number: int=None):
        self.number = number
    @property
    def msg_text(self):
        return f'Не нашёл анекдота под номером {self.number}.'
class AnecdoteDeletionNumberError(AnecdoteRequestError):
    msg_text = f'Если вы пытаетесь удалить анекдот, то я не понял его номер. ' + \
                'Чтобы я его понял, нужно чтобы в сообщении не было чисел, кроме номера анекдота, ' + \
                'или чтобы нужное число было последним словом в сообщении'

class DevUtilsError(Error):
    pass
class DevUtilsRequestError(DevUtilsError, RequestError):
    pass
class MethodError(DevUtilsError):
    pass
class InvalidMethodNameError(MethodError):
    def __init__(self, method_word: str=...) -> None:
        self.method_word = method_word
    @property
    def msg_text(self):
        return f'Не нашел в себе функцию-обработчик {self.method_word}'
class NoArgsMethodError(MethodError):
    def __init__(self, method) -> None:
        self.method = method
    @property
    def msg_text(self):
        return f'{self.method.__annotations__}'
class MethodArgsInvalidError(MethodError):
    def __init__(self, arg_word: str, needed_type: type, pos: int=..., extra_message: str=...):
        self.arg_word = arg_word
        self.needed_type = needed_type
        self.pos = pos
        self.extra_message = extra_message
    @property
    def msg_text(self):
        return f'{self.arg_word} {f"({self.pos}-й аргумент) " if self.pos else ""}' + \
            f'должен быть конвертируемым в {self.needed_type}.{f" ({self.extra_message})" if self.extra_message else ""}'
class NoMethodError(MethodError):
    @property
    def msg_text(self):
        return 'Доступные методы:\n' + '\n'.join(handlers.__all__)
