
def is_word_groop_name(word: str):
    return word in ('1', '2') or 'перв' in word or 'втор' in word

def find_groupword(text: str):
    if '1' in text or 'перв' in text: 
        return 1
    if '2' in text or 'втор' in text: 
        return 2
    return 0

def find_group_in_text(text: str, return_end_pos: bool=False):
    group = 0
    if group_pos := text.find('груп'):
        find_in: str = text[:group_pos].strip()
        group = find_groupword(find_in)
        if return_end_pos:
            end_pos = group_pos
            for s in text[group_pos:]:
                end_pos += 1
                if s == ' ':
                    break
            return group, end_pos
        return group
    return group


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
    import pprint
    pprint.pprint(photos)
    if not photos: 
        return ''
    return photos[0].file_id
    string = ''
    for i in photos:
        string += i.file_id + ','
    if string.endswith(','): 
        string = string[:-1]
    string = ','.join(list(set(string.split(','))))
    return string 

def str_to_photos(string_attachment: str, caption: str=None) -> list:
    """Formats `string_attachment` to list of `InputMediaPhoto` instaces. Sets caption on `caption` if exisits"""
    from aiogram.types import InputMediaPhoto
    return list(map(
            lambda p: InputMediaPhoto(media=p, caption=caption), 
            string_attachment.split(',')
            ))
