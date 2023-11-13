
import handlers
from types import FunctionType
from exceptions import InvalidMethodNameError, NoArgsMethodError, MethodArgsInvalidError, NoMethodError
import datetime

def dev_method_ttt(text: str):
    # parse
    words = text[1:].split()
    if len(words) == 1 and words[0] == 'метод':
        raise NoMethodError()
    method_word = words[1]
    method: FunctionType = handlers.__dict__.get(method_word, None)
    if method is None:
        raise InvalidMethodNameError(method_word)
    if len(words) == 2:
        raise NoArgsMethodError(method)
    args = text[text.find('_ttt ') + 5:].split(';')
    for i, key in enumerate(method.__annotations__):
        if method.__annotations__[key] is str:
            ...
        else:
            try:
                if method.__annotations__[key] is int:
                    args[i] = int(args[i])
                elif method.__annotations__[key] is datetime.datetime:
                    args[i] = datetime.datetime.fromisoformat(args[i]) # 'YYYY-MM-DD HH:MM:SS.mmmmmm'
                elif method.__annotations__[key] is bool:
                    if args[i].lower() == 'true':
                        args[i] = True
                    if args[i].lower() == 'false':
                        args[i] = False
                    else:
                        raise TypeError('Bool value must be "True" or "False')
            except (TypeError, ValueError) as ex:
                raise MethodArgsInvalidError(args[i], method.__annotations__[key], i + 1, ex)

    result = method(*args)
    result = tuple(map(str, result))

    return result
            