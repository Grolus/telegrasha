import data.config as config
import logging
import asyncio
import sys
import time
import os
import re
import random

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, Update
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import F
from typing import Sequence
from pprint import pprint
from dp import dp
from subject import ALL_SUBJECTS, GROOPED_SUBJECTS, ALL_TIMETABLES, Homework
from anecdote import Anecdote
from utils import *

# log
logging.basicConfig(level=logging.INFO)


IS_W_FOR_GROUP = False
WEEKDAYS_GEN = ['понедельник', 'вторник', 'среду', 'четверг', 'пятницу', 'субботу', 'воскресение']
WEEKDAYS_CALLS = ['понед', 'вторник', 'сред', 'четверг', 'пятниц', 'суббот', 'воскр']
IS_ON_SERVER = 'Grolus' in os.path.abspath(__file__)



@dp.message(F.text.lower() == 'аркаша?')
async def self_call(msg: Message):
    logging.info('Self call detected')
    await msg.answer(f'Я тут, {msg.from_user.full_name}')

hw_set_regex = r'^[пП]о .+|.+ [пП]о \S+(?: [12] групп?[аые])?$'
filters = F.text.regexp(hw_set_regex) | F.photo & F.caption.regexp(hw_set_regex)
@dp.message(filters)
@dp.edited_message(filters)
async def homework_set(msg: Message):
    logging.info('Homework setting')

    text = msg.text.lower() if msg.text else msg.caption.lower()
    text_words = text.split()
    is_simple = text.startswith('по ')
    is_grooped_in_msg = len(text_words) > 4 and (('груп' in text_words[3] and is_word_groop_name(text_words[2])) or \
        ('груп' in text_words[-1] and is_word_groop_name(text_words[-2])))
    
    # subject searching
    sj_searched_in = text.split()[1] + ' ' + text.split()[-1]
    for subject in ALL_SUBJECTS:
        for alias in subject.aliases:
            if alias in sj_searched_in:
                break
        else:
            continue
        break
    else:
        return # :(
    
    # group searchig
    weekdays_key = None
    group = None
    if subject in GROOPED_SUBJECTS:
        if is_grooped_in_msg:
            if (group := word_to_group(text_words[2])) or (group := word_to_group(text_words[-1])):
                weekdays_key = group - 1
        if weekdays_key is None:
            await msg.answer(
f'''Не понял, какая группа предмета {subject.name_ru} вам нужна. 
Повторите (или измените исходное) сообщение по шаблону: 
по [предмет] [номер группы] группа ...'''
            )
            return

    # text compile
    text_words = msg.text.split() if msg.text else msg.caption.split()
    if text.startswith('по '):
        hw_text_words = text_words[4:] if is_grooped_in_msg else text_words[2:] 
    else:
        hw_text_words = text_words[:-2]
    hw_text = ' '.join(hw_text_words)
    hw_text = hw_text.strip()
    if hw_text.startswith('-'): hw_text = hw_text[1:]

    # time compile
    now_week, now_weekday = get_now_week_weekday()
    new_week, new_weekday = wd_calc(now_week, now_weekday, subject.weekdays[weekdays_key] if subject.is_grouped else subject.weekdays)

    # attachment saving
    attachment = ''
    if msg.photo:
        attachment = msg.photo[0].file_id

    # homework saving
    collected_homework = Homework(subject, hw_text, msg.from_user.full_name, attachment)
    if not collected_homework.save(new_week, new_weekday, group):
        await msg.answer(f'Не удалось сохранить дз по {subject.name_ru}')
        return
    await msg.answer(f'Сохранил задание по {subject.name_ru}{f" ({group} группа)" if group else ""}' + \
                     f' на {WEEKDAYS_GEN[new_weekday]}{" следующей недели" if new_week > now_week else ""}' + \
                     f' [{hw_text}] Спасибо')

hw_request_regex = r'[Чч]то (?:по|на) .*\?$'
@dp.message(F.text.regexp(hw_request_regex))
@dp.edited_message(F.text.regexp(hw_request_regex))
async def homework_request(msg: Message):
    text = msg.text.lower()
    text_words = text.split()
    is_grooped_in_msg = len(text_words) > 3 and is_word_groop_name(text_words[3])
    # subject searching
    for subject in ALL_SUBJECTS:
        for alias in subject.aliases:
            if len(text_words) > 2 and alias in text_words[2]:
                break
        else:
            continue
        break
    else:
        return
    
    # group searching
    weekdays_key = None
    group = None
    if subject in GROOPED_SUBJECTS:
        if is_grooped_in_msg:
            if group := word_to_group(text_words[3]):
                weekdays_key = group - 1
        if weekdays_key is None:
            await msg.answer(
f'''Не понял, какая группа предмета {subject.name_ru} вам нужна. 
Повторите (или измените исходное) сообщение по шаблону: 
"по [предмет] [номер группы] группа ..."'''
            )
            return

    # time compile
    now_week, now_weekday = get_now_week_weekday()
    new_week, new_weekday = wd_calc(now_week, now_weekday, subject.weekdays[weekdays_key] if subject.is_grouped else subject.weekdays)
    
    # homework loading 
    if not (loaded_homework := subject.load(new_week, new_weekday, group)):
        await msg.answer(f'Не найдено задания по {subject.name_ru}{f" ({group} группа)" if group else ""}.')
        return
    answer = f'Задание по {subject.name_ru}{f" ({group} группа)" if group else ""}' +\
            f' на {WEEKDAYS_GEN[new_weekday]}{" следующей недели" if new_week > now_week else ""}:\n' +\
            f'{loaded_homework.text} (отправил(а): {loaded_homework.sender})'
    if loaded_homework.attachment:
        await msg.answer_photo(loaded_homework.attachment, answer)
        return
    await msg.answer(f'Задание по {subject.name_ru}{f" ({group} группа)" if group else ""}' +\
                     f' на {WEEKDAYS_GEN[new_weekday]}{" следующей недели" if new_week > now_week else ""}:\n' +\
                     f'{loaded_homework.text} (отправил(а): {loaded_homework.sender})')

hw_full_request_regex = r'[Чч]то задали на .+\?$'
@dp.message(F.text.regexp(hw_full_request_regex))
async def full_homework_request(msg: Message):
    text = msg.text.lower()
    text_words = text.split()

    # time compile
    weekday = None
    for i, call in enumerate(WEEKDAYS_CALLS):
        if call in text:
            weekday = i
            break
    now_week, now_weekday = get_now_week_weekday()
    if weekday is None:
        if 'сегодня' in text:
            weekday = now_weekday
        elif 'завтра' in text:
            weekday = wd_up(now_weekday, 1)
        else:
            await msg.answer(f'Чтобы узнать дз на весь день, напишите "что задали на [день недели]?"')
            return
    if weekday > 4:
        await msg.answer(f'Очень смешно, но у нас пятидневка')
        return
    week = wd_calc(now_week, now_weekday, [weekday])[0]

    # answer compile
    subjects_to_load_hw = ALL_TIMETABLES[weekday].subjects
    answer = f'Домашнее задание на {WEEKDAYS_GEN[weekday]}:\n'
    for i, subject in enumerate(subjects_to_load_hw):
        line = f'{i+1}. '
        if isinstance(subject, Sequence):
            for i, s in enumerate(subject):
                if hw := s.load(week, weekday, i+1):
                    line += f'{s.name_ru}{f" (c вложением)" if hw.attachment else ""}: {hw.text}\n'
                else:
                    line += f'{s.name_ru} не найдено\n'
                line += '   '
        else:
            if hw := subject.load(week, weekday):
                line += f'{subject.name_ru}{f" (c вложением)" if hw.attachment else ""}: {hw.text}\n'
            else:
                line += f'{subject.name_ru} не найдено\n'
        answer += f'{line}\n'
    await msg.answer(answer)

@dp.message(F.text.regexp(r'[Аа]некдот(?: ?[-:].+)?$', flags=16))
async def anecdote_set(msg: Message):
    # text parse
    if msg.reply_to_message and len(msg.text.split()) == 1:
        anec_text = msg.reply_to_message.text
        if anec_text is None:
            anec_text = msg.reply_to_message.caption
    else:
        anec_text = msg.text[8:] if len(msg.text) > 8 else None
    
    # saving anecdote
    number = Anecdote.save(anec_text)
    # answer
    if anec_text is None: 
        await msg.answer(f'''Если вы пытались сохранить анекдот, то что то пошло не так. 
                         Ответьте на сообщение с анекдотом сообщением "Анекдот" или напишите его сами: 
                         "Анекдот: [текст анекдота]"''')
    await msg.answer(f'Сохранил анекдот [{anec_text}]. Спасибо, это уже мой {number}-й анекдот.')

@dp.message(F.text.regexp(r'^[Аа]ркаша?,? расс?кажи анек(?:дот)?.*(?: \d+)?$'))
async def anecdote_request(msg: Message):
    psewdo_number = msg.text.split()[-1]
    if psewdo_number.isdigit():
        number = int(psewdo_number)
    else:
        now_anecdotes = Anecdote.get_all_numbers()
        if not now_anecdotes:
            await msg.answer(f'К сожалению, у меня нет анекдотов :( Но ты можешь его записать! Просто напиши "Анекдот: [сам анекдот]"')
            return
        number = random.choice(now_anecdotes)
    anecdote = Anecdote.get(number)
    if anecdote is None:
        await msg.answer(f'Не нашёл анекдота под номером {number}.')
        return
    await msg.answer(f'Анекдот {number}: \n{anecdote}')

@dp.message(F.text.regexp(r'[Аа]ркаша?,? уд[ао]ли (?:[0-9]* )?анек(?:дот)?.*'))
async def anecdote_deletion_request(msg: Message):
    psewdo_number = msg.text.split()[-1]
    if psewdo_number.isdigit():
        number = int(psewdo_number)
    elif len(numbers := find_numbers_in_text(msg.text)) == 1:
        number = numbers[0]
    else:
        await msg.answer(f'Если вы пытаетесь удалить анекдот, то я не понял его номер. ' + \
                         'Чтобы я его понял, нужно чтобы в сообщении не было чисел, кроме номера анекдота, ' + \
                            'или чтобы нужное число было последним словом в сообщении')
        return
    if not Anecdote.delete(number):
        await msg.answer(f'Не нашёл анекдота под номером {number}.')
        return
    await msg.answer(f'Успешно удалён анекдот под номером {number}.')
    



async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    session = AiohttpSession(proxy="http://proxy.server:3128")
    bot = Bot(token=config.arkadiy_tg_token, session=session if IS_ON_SERVER else None)
    # And the run events dispatching
    await bot.send_message(1122505805, f'Я запустился ({time.ctime()})')
    await dp.start_polling(bot)

# run long-polling
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())