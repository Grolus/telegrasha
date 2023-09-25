import config
import logging
import asyncio
import sys
import time
import re

from aiogram import Bot, Dispatcher, types
from aiogram.types.message import ContentType
from aiogram import F
from dp import dp
from subject import ALL_SUBJECTS, GROOPED_SUBJECTS, Homework
from utils import *

# log
logging.basicConfig(level=logging.INFO)


IS_W_FOR_GROUP = False
WEEKDAYS_GEN = ['понедельник', 'вторник', 'среду', 'четверг', 'пятницу', 'субботу', 'воскресение']


@dp.message(F.text == 'аркаша?')
async def self_call(msg: types.Message):
    logging.info('Self call detected')
    await msg.answer(f'Я тут, {msg.from_user.full_name}')


hw_set_regex = r'^[пП]о .+|.+ [пП]о \S+(?: [12] групп?[аые])$'
@dp.message(F.text.regexp(hw_set_regex))
@dp.edited_message(F.text.regexp(hw_set_regex))
async def homework_set(msg: types.Message):
    logging.info('Homework setting')
    text = msg.text.lower()
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
        return
    
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
    if text.startswith('по '):
        hw_text_words = text_words[4:] if is_grooped_in_msg else text_words[2:] 
    else:
        hw_text_words = text_words[:-2]
    hw_text = ' '.join(hw_text_words)
    if hw_text.startswith('-'): hw_text[1:]

    # time compile
    now_weekday = msg.date.weekday()
    now_week = time.gmtime(msg.date.toordinal()).tm_yday // 7 + 1
    new_week, new_weekday = wd_calc(now_week, now_weekday, subject.weekdays[weekdays_key] if subject.is_grouped else subject.weekdays)

    # homework saving
    collected_homework = Homework(subject, hw_text, msg.from_user.full_name)
    if not collected_homework.save(new_week, new_weekday, group):
        await msg.answer(f'Не удалось сохранить дз по {subject.name_ru}')
        return
    await msg.answer(f'Сохранил задание по {subject.name_ru}{f" ({group} группа)" if group else ""}' +\
                     f' на {WEEKDAYS_GEN[new_weekday]}{" следующей недели" if new_week > now_week else ""}' +\
                     f' ({hw_text}). Спасибо')


hw_request_regex = r'[Чч]то (?:по |на ).*\?$'
@dp.message(F.text.regexp(hw_request_regex))
@dp.edited_message(F.text.regexp(hw_request_regex))
async def homework_request(msg: types.Message):
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
по [предмет] [номер группы] группа ...'''
            )
            return

    # time compile
    now_weekday = msg.date.weekday()
    now_week = time.gmtime(msg.date.toordinal()).tm_yday // 7 + 1
    new_week, new_weekday = wd_calc(now_week, now_weekday, subject.weekdays[weekdays_key] if subject.is_grouped else subject.weekdays)
    
    # homework loading
    if not (loaded_homework := subject.load(new_week, new_weekday, group)):
        await msg.answer(f'Не найдено задания по {subject.name_ru}{f" ({group} группа)" if group else ""}.')
        return
    await msg.answer(f'Задание по {subject.name_ru}' +\
                     f' на {WEEKDAYS_GEN[new_weekday]}{" следующей недели" if new_week > now_week else ""}:\n' +\
                     f'{loaded_homework.text} (отправил(а): {loaded_homework.sender})')

# echo
@dp.message()
async def echo(msg: types.Message):
    logging.info('Echo answered')
    await msg.answer(f'{msg.text}')

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(token=config.arkadiy_tg_token)
    # And the run events dispatching
    await bot.send_message(1122505805, f'Я запустился ({time.ctime()})')
    await dp.start_polling(bot)

# run long-polling
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())