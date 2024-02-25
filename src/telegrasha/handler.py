
from dispatcher import dispatcher
from aiogram import F
from aiogram.types import Message
from handlers import *
from dev_utils import dev_method_ttt, dev_time_ttt
from typing import Sequence
from utils.subject import is_subject_in, Homework, hw_tuple_to_line
from utils.constants import WEEKDAYS_GENITIVE
from utils.tools import str_to_photos
from config import SELF_CALL_REGEXP
from exceptions import (GroupNotFoundError, HomeworkSettingError,
                        HomeworkNotFoundError, WeekWeekdayNotFoundError, AnecdoteRequestError,
                        NoAnecdotesError, AnecdoteNotFoundError, AnecdoteDeletionNumberError,
                        DevUtilsError, RequestError, Error)
import sys


devut_method_regex = r'^!метод.*$'
@dispatcher.message(F.text.regexp(devut_method_regex))
@dispatcher.edited_message(F.text.regexp(devut_method_regex))
async def dev_method(msg: Message):
    try:
        result = dev_method_ttt(msg.text)
    except DevUtilsError as ex:
        answer = ex.msg_text
    except RequestError as ex:
        answer = ex.msg_text
    except TypeError as ex:
        answer = f'Ошибка: {ex}'
    else:
        answer = f'{result}'
    finally:
        await msg.answer(answer)

@dispatcher.message(F.text.regexp(r'^!время.*$'))
async def dev_time(msg: Message):
    try:
        result = dev_time_ttt(msg.text, msg.date)
    except Exception as ex:
        answer = f'Ошибка: {ex}'
    else:
        answer = f'{result[0].isoformat(sep=" ")}.\nНеделя: {result[1]}\nДень: {result[2]}'
    finally:
        await msg.answer(answer)

@dispatcher.message(F.text.lower() == 'аркаша?')
async def self_call(msg: Message):
    result = self_call_ttt(msg.text, 
                           sender=msg.from_user.full_name)
    answer = f'Я тут, {result[0]}'
    await msg.reply(answer)

hw_set_regex = r'^' + SELF_CALL_REGEXP + r',? ?(?:дз |задание )?[пП]о .*[^?]$'
filter = (F.text.regexp(hw_set_regex) & F.text.func(is_subject_in)) | \
    (F.photo & F.caption.regexp(hw_set_regex) & F.caption.func(is_subject_in))
@dispatcher.message(filter)
@dispatcher.edited_message(filter)
async def homework_set(msg: Message):
    try:
        result = homework_set_ttt(msg.text or msg.caption, 
                                  attachment=msg.photo,
                                  sender=msg.from_user.full_name,
                                  date=msg.date)

    except HomeworkSettingError as ex:
        answer = ex.msg_text
    except HomeworkNotFoundError as ex:
        answer = ex.msg_text
    except Exception as ex:
        answer = f'Ошибка ({msg.chat.id}): {ex if msg.chat.id != 1122505805 else "+" + str(ex.with_traceback(sys.exc_info()[2]))}'
    else:
        answer = f'Сохранил задание по {result[0].name_ru}{f" ({result[1]} группа)" if result[1] else ""}' + \
                 f' на {WEEKDAYS_GENITIVE[result[3]]}{" следующей недели" if result[4] else ""}' + \
                 f' [{result[5].text}]. Спасибо'
    finally:
        await msg.answer(answer)

hw_request_regex = r'[Чч]то (?:по|на) .*\?$'
@dispatcher.message(F.text.regexp(hw_request_regex) & F.text.func(is_subject_in))
@dispatcher.edited_message(F.text.regexp(hw_request_regex))
async def homework_request(msg: Message):
    attachment = None
    try:
        result = homework_request_ttt(msg.text, date=msg.date)
    except GroupNotFoundError as ex:
        answer = ex.msg_text
    except HomeworkNotFoundError as ex:
        answer = ex.msg_text
    else:
        answer = f'Задание по {result[0].subject.name_ru}{f" ({result[1]} группа)" if result[1] else ""}' +\
                f' на {WEEKDAYS_GENITIVE[result[3]]}{" следующей недели" if result[4] else ""}:\n' +\
                f'{result[0].text} (отправил(а): {result[0].sender})'
        attachment = result[0].attachment
    finally:
        if attachment:
            if result[0].is_attachment_multiple:
                await msg.answer_media_group(str_to_photos(attachment, answer))
            else: 
                await msg.answer_photo(attachment, answer)
        else:
            await msg.answer(answer)

hw_full_request_regex = r'[Чч]то задали на .+\?$'
@dispatcher.message(F.text.regexp(hw_full_request_regex))
async def full_homework_request(msg: Message):
    try:
        result = full_homework_request_ttt(msg.text, date=msg.date)
    except Error:
        answer = msg.text
    except Exception as ex:
        answer = f'Ошибка: {ex}'
        print(ex.with_traceback())
    else:
        answer = f"Задание на {WEEKDAYS_GENITIVE[result[1]]}{' следующей недели' if result[2] else ''}:\n" + '\n'.join(
            [Homework.to_line(hw, i+1) if not isinstance(hw, Sequence) 
             else hw_tuple_to_line(hw, i+1)
             for i, hw in enumerate(result[3])]
        )
    finally:
        await msg.answer(answer)

@dispatcher.message(F.text.regexp(r'^' + SELF_CALL_REGEXP[:-1] + r' реши .*(?: [0-9]{1-4})+'))
async def gdz_request(msg: Message):
    ...

@dispatcher.message(F.text.regexp(r'[Аа]некдот(?: ?[-:].+)?$', flags=16))
async def anecdote_set(msg: Message):
    try:
        result = anecdote_set_ttt(msg.text, is_reply=not not msg.reply_to_message, 
                              reply_message_text=msg.reply_to_message.text if msg.reply_to_message else None)
    except AnecdoteRequestError as ex:
        answer = ex.msg_text
    else:
        answer = f'Сохранил анекдот [{result[1][:15] + "..." if len(result[1]) > 15 else result[1]}]. ' + \
                 f'Спасибо, это уже мой {result[0]}-й анекдот.'
    finally: 
        await msg.answer(answer)

@dispatcher.message(F.text.regexp(r'^' + SELF_CALL_REGEXP + r',? расс?кажи анек(?:дот)?.*(?: \d+)?$'))
async def anecdote_request(msg: Message):
    try:
        result = anecdote_request_ttt(msg.text)
    except NoAnecdotesError as ex:
        answer = ex.msg_text
    except AnecdoteNotFoundError as ex:
        answer = ex.msg_text
    else:
        answer = f'Анекдот {result[0]}: {result[1]}'
    await msg.answer(answer)

@dispatcher.message(F.text.regexp(r'^' + SELF_CALL_REGEXP + r',? уд[ао]ли (?:[0-9]* )?анек(?:дот)?.*'))
async def anecdote_deletion_request(msg: Message):
    try:
        result = anecdote_deletion_request_ttt(msg.text)
    except AnecdoteNotFoundError as ex:
        answer = ex.msg_text
    except AnecdoteDeletionNumberError as ex:
        answer = ex.msg_text
    else:
        answer = f'Успешно удалён анекдот под номером {result[0]}.'
    await msg.answer(answer)

