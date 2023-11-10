
from aiogram.types import InputMediaPhoto

def is_word_groop_name(word: str):
    return word in ('1', '2') or 'перв' in word or 'втор' in word

def word_to_group(word):
    if word == '1' or 'перв' in word: return 1
    if word == '2' or 'втор' in word: return 2
    return 0

def find_numbers_in_text(text: str) -> list[int]:
    """Ищет числа в тексте и возвращает их список"""
    numbers = []
    current_number = ''
    saving = False
    for s in text:
        if s.isdigit() and saving:
            current_number += s
        elif s.isdigit():
            saving = True
            current_number += s
        else:
            saving = False
            if current_number:
                numbers.append(int(current_number))
            current_number = ''
    if current_number:
        numbers.append(int(current_number))
    return numbers

def photos_to_str(photos: list):
    string = ''
    for i in photos:
        string += i.file_id + ','
    if string.endswith(','): string = string[:-1]
    return string

def str_to_photos(string_attachment: str, caption: str=None) -> list[InputMediaPhoto]:
    """Formats `string_attachment` to list of `InputMediaPhoto` instaces. Sets caption on `caption` if exisits"""
    return list(map(
            lambda p: InputMediaPhoto(media=p, caption=caption), 
            string_attachment.split(',')
            ))
