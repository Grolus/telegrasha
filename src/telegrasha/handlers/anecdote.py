

import random
from utils.anecdote import Anecdote
from utils.tools import find_numbers_in_text
from logers import anecdote as loger
from exceptions import AnecdoteRequestError, NoAnecdotesError, AnecdoteNotFoundError, AnecdoteDeletionNumberError


def anecdote_set_ttt(text: str, is_reply: bool, reply_message_text: str) -> tuple[int, str]:
    """Sets anecdote from `text`. Also can save from `reply_message_text`.\n
    On succes returns tuple: (`number`, `anec_text`)"""
    # text parse
    if is_reply and len(text.split()) == 1:
        anec_text = reply_message_text
    else:
        anec_text = text[8:] if len(text) > 8 else None
    # saving anecdote
    if anec_text is None:
        raise AnecdoteRequestError
    number = Anecdote.save(anec_text)
    # answer
    return (number, anec_text)

def anecdote_request_ttt(text: str) -> tuple[int, str]:
    """Loads and returns anecdote by number parsed from `text`.
    If number not exists, loads random anecdote. \n
    On succes returns tuple: (`number`, `anecdote`)"""
    psewdo_number = text.split()[-1]
    if psewdo_number.isdigit():
        number = int(psewdo_number)
    else:
        now_anecdotes = Anecdote.get_all_numbers()
        if not now_anecdotes:
            raise NoAnecdotesError
        number = random.choice(now_anecdotes)
    anecdote = Anecdote.get(number)
    if anecdote is None:
        raise AnecdoteNotFoundError(number)
    return (number, anecdote)


def anecdote_deletion_request_ttt(text: str):
    psewdo_number = text.split()[-1]
    if psewdo_number.isdigit():
        number = int(psewdo_number)
    elif len(numbers := find_numbers_in_text(text)) == 1:
        number = numbers[0]
    else:
        raise AnecdoteDeletionNumberError()
    if not Anecdote.delete(number):
        raise AnecdoteNotFoundError(number)
    
    return tuple(number)

