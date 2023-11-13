
def self_call_ttt(text: str='what?', sender: str='how?') -> tuple[str]:
    """Returns just a tuple with (`sender`)"""
    #logging.info(f'Self call detected ({time.gmtime(msg.date.timestamp())})')
    return (sender, )
