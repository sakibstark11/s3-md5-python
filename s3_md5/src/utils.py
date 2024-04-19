'''basic converter utilities'''


def bytes_to_mega_bytes(value: int) -> float:
    '''convert bytes to megabytes'''
    return value / (1000 * 1000)


def seconds_to_minutes(value: float) -> float:
    '''convert seconds to minutes'''
    return value / 60
