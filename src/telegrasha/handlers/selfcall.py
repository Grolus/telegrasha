
def self_call_ttt(text: str, sender: str) -> tuple[str]:
    """Returns just a tuple with (`sender`)"""
    #logging.info(f'Self call detected ({time.gmtime(msg.date.timestamp())})')
    return (sender, )
