import os





class Anecdote:
    def save(text: str):
        if 'anecdotes' not in os.listdir('data'):
            os.mkdir('data/anecdotes')
        already_saved = os.listdir('data/anecdotes')
        if already_saved:
            already_saved_numbers = list(map(lambda s: int(s.split('.')[0]), already_saved))
            number = max(already_saved_numbers) + 1
        else:
            number = 1
        # saving
        file_path = f'data/anecdotes/{number}.txt'
        with open(file_path, 'w') as file:
            file.write(text)
        return number
    def get(number: int) -> str:
        """Возвращает анекдот по номеру"""
        if 'anecdotes' not in os.listdir('data'): return
        already_saved = os.listdir('data/anecdotes')
        if not already_saved: return
        already_saved_numbers = list(map(lambda s: int(s.split('.')[0]), already_saved))
        if not number in already_saved_numbers: return
        with open(f'data/anecdotes/{number}.txt', 'r') as file:
            anecdote = file.read()
        return anecdote
    def delete(number: int) -> bool:
        """Удаляет анекдот по номеру и возвращает `True`. \n
        Если данного анкдота под данным номером не было, то вернет `False`"""
        try:
            os.remove(f'data/anecdotes/{number}.txt')
            return True
        except FileNotFoundError:
            return False
    def get_all_numbers() -> list[int]:
        """Возвращает все номера записанных анекдотов"""
        if 'anecdotes' not in os.listdir('data'): return
        already_saved = os.listdir('data/anecdotes')
        if not already_saved: return
        already_saved_numbers = list(map(lambda s: int(s.split('.')[0]), already_saved))
        return already_saved_numbers

