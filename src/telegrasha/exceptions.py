
class Error(BaseException):
    msg_text = None
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
    """Homework can`t be empty"""
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

class WeekWeekdayNotFoundError(RequestError):
    pass

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


